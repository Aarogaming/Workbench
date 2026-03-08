#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Fetch standard Workbench incident artifacts from a GitHub Actions run.

Usage:
  bash scripts/fetch_workbench_artifacts.sh --run-id <RUN_ID> [options]

Options:
  --repo <OWNER/REPO>      GitHub repository. If omitted, derive from git remote.
  --run-id <RUN_ID>        GitHub Actions run id (required).
  --incident-id <ID>       Incident id used for cutover path naming.
  --run-attempt <N>        Run attempt used for cutover path naming.
  --class <CLASS>          Artifact class. Repeatable.
                           Supported: eval, attestations, policy, scorecards, gates, all
  --out-dir <PATH>         Destination root override.
                           Defaults:
                           - artifacts/cutover/<incident_id>/<run_id>-a<run_attempt> (when incident/attempt provided)
                           - artifacts/fetch/<run_id> (otherwise)
  --dry-run                Print commands without executing `gh`.
  -h, --help               Show this help message.
EOF
}

derive_repo_from_remote() {
  local remote
  remote="$(git remote get-url origin 2>/dev/null || true)"
  if [[ "$remote" =~ github\.com[:/]([^/]+/[^/.]+)(\.git)?$ ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

is_supported_class() {
  case "$1" in
    eval | attestations | policy | scorecards | gates | all)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

artifact_for_class() {
  case "$1" in
    eval)
      printf '%s\n' "nightly-eval-report"
      ;;
    attestations)
      printf '%s\n' "attestation-verify-report"
      ;;
    policy | gates)
      printf '%s\n' "workflow-policy-reports"
      ;;
    scorecards)
      printf '%s\n' "scorecard-results"
      ;;
    *)
      return 1
      ;;
  esac
}

ensure_unique_classes() {
  local input=("$@")
  local seen=" "
  local deduped=()
  local c
  for c in "${input[@]}"; do
    if [[ "$seen" != *" $c "* ]]; then
      deduped+=("$c")
      seen+=" $c "
    fi
  done
  printf '%s\n' "${deduped[@]}"
}

normalize_out_dir_path() {
  local raw="$1"
  local normalized="${raw//\\//}"
  if command -v cygpath >/dev/null 2>&1; then
    if [[ "$normalized" =~ ^[A-Za-z]:/ ]]; then
      cygpath -u "$normalized"
      return 0
    fi
  fi
  if [[ "$normalized" =~ ^([A-Za-z]):/(.*)$ ]]; then
    local drive
    drive="${BASH_REMATCH[1],,}"
    local rest
    rest="${BASH_REMATCH[2]}"
    printf '/mnt/%s/%s\n' "$drive" "$rest"
    return 0
  fi
  if [[ "$normalized" =~ ^([A-Za-z]):Users(.+)$ ]]; then
    local drive
    drive="${BASH_REMATCH[1],,}"
    local rest
    rest="Users${BASH_REMATCH[2]}"

    if [[ "$rest" =~ ^Users([^/]+)AppData(.*)$ ]]; then
      rest="Users/${BASH_REMATCH[1]}/AppData${BASH_REMATCH[2]}"
    fi
    if [[ "$rest" =~ ^(Users/.+/AppData)Local(.*)$ ]]; then
      rest="${BASH_REMATCH[1]}/Local${BASH_REMATCH[2]}"
    fi
    if [[ "$rest" =~ ^(Users/.+/AppData/Local)Temp(.*)$ ]]; then
      rest="${BASH_REMATCH[1]}/Temp${BASH_REMATCH[2]}"
    fi
    if [[ "$rest" =~ ^(Users/.+/AppData/Local/Temp)([^/].+)$ ]]; then
      rest="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    fi
    if [[ "$rest" =~ ^(.+)cutover$ ]] && [[ "$rest" != "cutover" ]]; then
      rest="${BASH_REMATCH[1]}/cutover"
    fi
    printf '/mnt/%s/%s\n' "$drive" "$rest"
    return 0
  fi
  printf '%s\n' "$normalized"
}

REPO=""
RUN_ID=""
INCIDENT_ID=""
RUN_ATTEMPT=""
OUT_DIR=""
DRY_RUN=0
CLASSES=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      [[ $# -ge 2 ]] || { echo "Error: --repo requires a value" >&2; exit 2; }
      REPO="$2"
      shift 2
      ;;
    --run-id)
      [[ $# -ge 2 ]] || { echo "Error: --run-id requires a value" >&2; exit 2; }
      RUN_ID="$2"
      shift 2
      ;;
    --incident-id)
      [[ $# -ge 2 ]] || { echo "Error: --incident-id requires a value" >&2; exit 2; }
      INCIDENT_ID="$2"
      shift 2
      ;;
    --run-attempt)
      [[ $# -ge 2 ]] || { echo "Error: --run-attempt requires a value" >&2; exit 2; }
      RUN_ATTEMPT="$2"
      shift 2
      ;;
    --class)
      [[ $# -ge 2 ]] || { echo "Error: --class requires a value" >&2; exit 2; }
      CLASSES+=("$2")
      shift 2
      ;;
    --out-dir)
      [[ $# -ge 2 ]] || { echo "Error: --out-dir requires a value" >&2; exit 2; }
      OUT_DIR="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument '$1'" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$RUN_ID" ]]; then
  echo "Error: --run-id is required" >&2
  usage >&2
  exit 2
fi

if [[ -n "$INCIDENT_ID" || -n "$RUN_ATTEMPT" ]]; then
  if [[ -z "$INCIDENT_ID" || -z "$RUN_ATTEMPT" ]]; then
    echo "Error: --incident-id and --run-attempt must be provided together" >&2
    exit 2
  fi
  if ! [[ "$RUN_ATTEMPT" =~ ^[0-9]+$ ]] || [[ "$RUN_ATTEMPT" -lt 1 ]]; then
    echo "Error: --run-attempt must be an integer >= 1" >&2
    exit 2
  fi
fi

if [[ -z "$REPO" ]]; then
  if ! REPO="$(derive_repo_from_remote)"; then
    echo "Error: unable to derive --repo from git remote; pass --repo explicitly" >&2
    exit 2
  fi
fi

if [[ ${#CLASSES[@]} -eq 0 ]]; then
  CLASSES=(eval attestations policy)
fi

for class_name in "${CLASSES[@]}"; do
  if ! is_supported_class "$class_name"; then
    echo "Error: unsupported class '$class_name'" >&2
    exit 2
  fi
done

if [[ " ${CLASSES[*]} " == *" all "* ]]; then
  CLASSES=(eval attestations policy scorecards)
fi

mapfile -t CLASSES < <(ensure_unique_classes "${CLASSES[@]}")

if [[ -z "$OUT_DIR" ]]; then
  if [[ -n "$INCIDENT_ID" && -n "$RUN_ATTEMPT" ]]; then
    OUT_DIR="artifacts/cutover/${INCIDENT_ID}/${RUN_ID}-a${RUN_ATTEMPT}"
  else
    OUT_DIR="artifacts/fetch/${RUN_ID}"
  fi
fi
OUT_DIR="$(normalize_out_dir_path "$OUT_DIR")"

WINDOWS_TARGET_OUT_DIR=""
if [[ "$OUT_DIR" =~ ^[A-Za-z]:/ ]]; then
  WINDOWS_TARGET_OUT_DIR="$OUT_DIR"
  OUT_DIR=".tmp/fetch_workbench/${RUN_ID}-$$"
fi

mkdir -p "$OUT_DIR"

if [[ "$DRY_RUN" -eq 0 ]] && ! command -v gh >/dev/null 2>&1; then
  echo "Error: GitHub CLI 'gh' is required (or use --dry-run)." >&2
  exit 2
fi

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  echo "Error: python3 or python is required to generate index.json" >&2
  exit 2
fi

RESULTS_FILE="${OUT_DIR}/fetch_summary.txt"
{
  echo "repo=${REPO}"
  echo "run_id=${RUN_ID}"
  echo "incident_id=${INCIDENT_ID}"
  echo "run_attempt=${RUN_ATTEMPT}"
  echo "dry_run=${DRY_RUN}"
  echo "classes=$(IFS=,; echo "${CLASSES[*]}")"
} >"$RESULTS_FILE"

FAILURES=0
INDEX_ROWS_FILE="${OUT_DIR}/.index_rows.tsv"
: >"$INDEX_ROWS_FILE"

for class_name in "${CLASSES[@]}"; do
  artifact_name="$(artifact_for_class "$class_name")"
  class_dir="${OUT_DIR}/${class_name}"
  mkdir -p "$class_dir"

  cmd=(gh run download "$RUN_ID" --repo "$REPO" --name "$artifact_name" --dir "$class_dir")
  if [[ "$DRY_RUN" -eq 1 ]]; then
    printf '[dry-run] class=%s' "$class_name"
    printf ' %q' "${cmd[@]}"
    printf '\n'
    echo "class=${class_name} artifact=${artifact_name} status=dry-run dir=${class_dir}" >>"$RESULTS_FILE"
    printf '%s\t%s\t%s\t%s\n' "$class_name" "$artifact_name" "dry-run" "$class_dir" >>"$INDEX_ROWS_FILE"
    continue
  fi

  echo "[fetch] class=${class_name} artifact=${artifact_name}"
  if "${cmd[@]}"; then
    echo "[ok] class=${class_name} artifact=${artifact_name}"
    echo "class=${class_name} artifact=${artifact_name} status=ok dir=${class_dir}" >>"$RESULTS_FILE"
    printf '%s\t%s\t%s\t%s\n' "$class_name" "$artifact_name" "ok" "$class_dir" >>"$INDEX_ROWS_FILE"
  else
    echo "[missing] class=${class_name} artifact=${artifact_name}" >&2
    echo "class=${class_name} artifact=${artifact_name} status=missing dir=${class_dir}" >>"$RESULTS_FILE"
    printf '%s\t%s\t%s\t%s\n' "$class_name" "$artifact_name" "missing" "$class_dir" >>"$INDEX_ROWS_FILE"
    FAILURES=1
  fi
done

INDEX_FILE="${OUT_DIR}/index.json"
"$PYTHON_BIN" - "$INDEX_ROWS_FILE" "$INDEX_FILE" "$REPO" "$RUN_ID" "$DRY_RUN" "$INCIDENT_ID" "$RUN_ATTEMPT" <<'PY'
import datetime as dt
import json
import sys
from pathlib import Path

rows_path = Path(sys.argv[1])
index_path = Path(sys.argv[2])
repo = sys.argv[3]
run_id = sys.argv[4]
dry_run = bool(int(sys.argv[5]))
incident_id = sys.argv[6] or None
run_attempt_raw = sys.argv[7]
run_attempt = int(run_attempt_raw) if run_attempt_raw else None

records = []
for raw_line in rows_path.read_text(encoding="utf-8").splitlines():
    if not raw_line.strip():
        continue
    class_name, artifact_name, status, dest = raw_line.split("\t", 3)
    records.append(
        {
            "class": class_name,
            "artifact_name": artifact_name,
            "status": status,
            "dir": dest,
        }
    )

payload = {
    "schema_version": "cp2.fetch_index.v1",
    "generated_at_utc": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "repo": repo,
    "run_id": run_id,
    "incident_id": incident_id,
    "run_attempt": run_attempt,
    "dry_run": dry_run,
    "artifacts": records,
}
index_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
PY
rm -f "$INDEX_ROWS_FILE"

if [[ -n "$WINDOWS_TARGET_OUT_DIR" ]]; then
  "$PYTHON_BIN" - "$OUT_DIR" "$WINDOWS_TARGET_OUT_DIR" <<'PY'
import shutil
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)

for item in src.iterdir():
    target = dst / item.name
    if item.is_dir():
        shutil.copytree(item, target, dirs_exist_ok=True)
    else:
        shutil.copy2(item, target)
PY
  RESULTS_FILE="${WINDOWS_TARGET_OUT_DIR}/fetch_summary.txt"
  INDEX_FILE="${WINDOWS_TARGET_OUT_DIR}/index.json"
fi

echo "[summary] ${RESULTS_FILE}"
echo "[index] ${INDEX_FILE}"
exit "$FAILURES"
