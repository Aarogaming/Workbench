#!/usr/bin/env python3
"""Run pytest for tests mapped to changed files."""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


EXPLICIT_TEST_MAPPINGS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("plugins/workflow_engine.py", ("test_phase0_smoke.py",)),
    ("plugins/mcp_auth.py", ("test_phase0_smoke.py",)),
    ("scripts/validate_workspace_index.py", ("test_validate_workspace_index.py",)),
    ("scripts/eval_report.py", ("test_eval_report.py",)),
    ("scripts/check_workflow_pinning.py", ("test_check_workflow_pinning.py",)),
    (
        "scripts/check_workflow_pinning_exceptions.py",
        ("test_check_workflow_pinning_exceptions.py",),
    ),
    ("scripts/check_scorecard_threshold.py", ("test_check_scorecard_threshold.py",)),
    ("scripts/verify_attestations.py", ("test_verify_attestations.py",)),
    ("scripts/update_scorecard_history.py", ("test_update_scorecard_history.py",)),
    ("scripts/check_secret_hygiene.py", ("test_check_secret_hygiene.py",)),
    ("scripts/check_plugin_contracts.py", ("test_check_plugin_contracts.py",)),
    (
        "scripts/validate_run_summary.py",
        ("test_validate_run_summary.py", "test_validate_run_summary_cli.py"),
    ),
    ("scripts/generate_run_summary.py", ("test_generate_run_summary.py",)),
    ("scripts/check_chimera_packets.py", ("test_check_chimera_packets.py",)),
    (
        "scripts/check_suggestions_bin_status.py",
        ("test_check_suggestions_bin_status.py",),
    ),
    (
        "scripts/generate_suggestions_bin_report.py",
        (
            "test_generate_suggestions_bin_report.py",
            "test_check_suggestions_bin_status.py",
            "test_run_quality_gates_plan.py",
        ),
    ),
    (
        "scripts/check_operations_nist_mapping.py",
        ("test_check_operations_nist_mapping.py",),
    ),
    (
        "scripts/check_ssdf_quality_gate_mapping.py",
        ("test_check_ssdf_quality_gate_mapping.py",),
    ),
    (
        "scripts/check_dora_reliability_scoreboard.py",
        ("test_check_dora_reliability_scoreboard.py",),
    ),
    (
        "scripts/check_campaign_wave_policy.py",
        ("test_check_campaign_wave_policy.py",),
    ),
    (
        "scripts/check_openai_async_policy.py",
        ("test_check_openai_async_policy.py",),
    ),
    (
        "scripts/check_jetstream_openai_campaign_policy.py",
        ("test_check_jetstream_openai_campaign_policy.py",),
    ),
    (
        "scripts/check_workflow_codeql_matrix_policy.py",
        ("test_check_workflow_codeql_matrix_policy.py",),
    ),
    (
        "scripts/check_reusable_workflow_governance_policy.py",
        ("test_check_reusable_workflow_governance_policy.py",),
    ),
    (
        "scripts/check_jetstream_consumer_openai_loop_policy.py",
        ("test_check_jetstream_consumer_openai_loop_policy.py",),
    ),
    (
        "scripts/check_dependency_review_policy.py",
        ("test_check_dependency_review_policy.py",),
    ),
    (
        "scripts/openai_retry_backoff.py",
        ("test_openai_retry_backoff.py",),
    ),
    (
        "scripts/evaluate_openai_compaction_threshold.py",
        ("test_evaluate_openai_compaction_threshold.py",),
    ),
    (
        "scripts/evaluate_jetstream_consumer_profile.py",
        ("test_evaluate_jetstream_consumer_profile.py",),
    ),
    (
        "scripts/openai_budget_preflight.py",
        ("test_openai_budget_preflight.py",),
    ),
    (
        "scripts/evaluate_promotion_watchtower.py",
        ("test_evaluate_promotion_watchtower.py",),
    ),
    (
        "scripts/generate_reusable_workflow_inventory.py",
        ("test_generate_reusable_workflow_inventory.py",),
    ),
    (
        "scripts/check_merge_queue_readiness.py",
        ("test_check_merge_queue_readiness.py",),
    ),
    (
        "scripts/check_merge_ruleset_deployment_guardrails.py",
        ("test_check_merge_ruleset_deployment_guardrails.py",),
    ),
    (
        "scripts/check_workflow_script_injection.py",
        ("test_check_workflow_script_injection.py",),
    ),
    (
        "scripts/check_dependency_inventory_forge_policy.py",
        ("test_check_dependency_inventory_forge_policy.py",),
    ),
    (
        "scripts/generate_dependency_inventory.py",
        ("test_generate_dependency_inventory.py",),
    ),
    (
        "scripts/compute_littles_law_wip.py",
        ("test_compute_littles_law_wip.py",),
    ),
    (
        "scripts/check_event_resilience_policy.py",
        ("test_check_event_resilience_policy.py",),
    ),
    (
        "scripts/check_async_eval_handoff_policy.py",
        ("test_check_async_eval_handoff_policy.py",),
    ),
    (
        "scripts/check_release_supply_chain_policy.py",
        ("test_check_release_supply_chain_policy.py",),
    ),
    (
        "scripts/check_cicd_telemetry_policy.py",
        ("test_check_cicd_telemetry_policy.py",),
    ),
    ("scripts/validate_fetch_index.py", ("test_validate_fetch_index.py",)),
    (
        "scripts/check_committed_run_summaries.py",
        ("test_check_committed_run_summaries.py",),
    ),
    ("scripts/select_failure_taxonomy.py", ("test_select_failure_taxonomy.py",)),
    ("scripts/fetch_workbench_artifacts.sh", ("test_fetch_workbench_artifacts.py",)),
    (
        "scripts/check_workflow_run_summary_wiring.py",
        ("test_check_workflow_run_summary_wiring.py",),
    ),
    (
        "scripts/check_workflow_operator_handoff_policy.py",
        ("test_check_workflow_operator_handoff_policy.py",),
    ),
    ("scripts/check_workflow_concurrency.py", ("test_check_workflow_concurrency.py",)),
    (
        "scripts/check_workflow_permissions_policy.py",
        ("test_check_workflow_permissions_policy.py",),
    ),
    ("scripts/check_gh_cli_version.py", ("test_check_gh_cli_version.py",)),
    (
        "scripts/check_attestation_preflight_wiring.py",
        ("test_check_attestation_preflight_wiring.py",),
    ),
    (
        "scripts/check_attestation_identity_wiring.py",
        ("test_check_attestation_identity_wiring.py",),
    ),
    (
        "scripts/check_attestation_offline_wiring.py",
        ("test_check_attestation_offline_wiring.py",),
    ),
    (
        "scripts/check_artifact_digest_wiring.py",
        ("test_check_artifact_digest_wiring.py",),
    ),
    (
        "scripts/check_artifact_retention_policy.py",
        ("test_check_artifact_retention_policy.py",),
    ),
    (
        "scripts/generate_artifact_digest_report.py",
        ("test_generate_artifact_digest_report.py",),
    ),
    (
        "scripts/verify_artifact_digests.py",
        ("test_verify_artifact_digests.py",),
    ),
    ("scripts/clean_cutover_artifacts.py", ("test_clean_cutover_artifacts.py",)),
    ("scripts/check_cp4b_sla.py", ("test_check_cp4b_sla.py",)),
    ("scripts/run_quality_gates.py", ("test_run_quality_gates_plan.py",)),
    (
        ".github/workflows/",
        (
            "test_check_workflow_run_summary_wiring.py",
            "test_check_workflow_concurrency.py",
            "test_check_workflow_permissions_policy.py",
            "test_check_attestation_preflight_wiring.py",
            "test_check_attestation_identity_wiring.py",
            "test_check_attestation_offline_wiring.py",
            "test_check_artifact_digest_wiring.py",
            "test_check_artifact_retention_policy.py",
            "test_check_operations_nist_mapping.py",
            "test_check_ssdf_quality_gate_mapping.py",
            "test_check_dora_reliability_scoreboard.py",
            "test_check_campaign_wave_policy.py",
            "test_check_openai_async_policy.py",
            "test_check_jetstream_openai_campaign_policy.py",
            "test_check_workflow_codeql_matrix_policy.py",
            "test_check_reusable_workflow_governance_policy.py",
            "test_check_jetstream_consumer_openai_loop_policy.py",
            "test_check_dependency_review_policy.py",
            "test_check_merge_queue_readiness.py",
            "test_check_merge_ruleset_deployment_guardrails.py",
            "test_check_workflow_script_injection.py",
            "test_check_dependency_inventory_forge_policy.py",
            "test_check_event_resilience_policy.py",
            "test_check_async_eval_handoff_policy.py",
            "test_check_release_supply_chain_policy.py",
            "test_check_cicd_telemetry_policy.py",
            "test_check_workflow_operator_handoff_policy.py",
            "test_check_suggestions_bin_status.py",
        ),
    ),
    (
        "docs/research/CHIMERA_V2_CP4B_NEXT_ACTIONS.md",
        ("test_check_cp4b_sla.py", "test_check_chimera_packets.py"),
    ),
    (
        "docs/research/CP_RUNBOOK_COMMANDS.md",
        (
            "test_check_chimera_packets.py",
            "test_check_merge_ruleset_deployment_guardrails.py",
            "test_check_dependency_inventory_forge_policy.py",
            "test_check_event_resilience_policy.py",
            "test_check_async_eval_handoff_policy.py",
            "test_check_release_supply_chain_policy.py",
            "test_check_cicd_telemetry_policy.py",
            "test_check_jetstream_openai_campaign_policy.py",
            "test_check_workflow_codeql_matrix_policy.py",
            "test_check_reusable_workflow_governance_policy.py",
            "test_check_jetstream_consumer_openai_loop_policy.py",
            "test_check_dependency_review_policy.py",
            "test_check_workflow_operator_handoff_policy.py",
            "test_check_suggestions_bin_status.py",
        ),
    ),
    ("docs/OPERATIONS.md", ("test_check_operations_nist_mapping.py",)),
    (
        "docs/research/SSDF_SP800_218_QUALITY_GATE_MAPPING.md",
        ("test_check_ssdf_quality_gate_mapping.py",),
    ),
    (
        "docs/SUGGESTIONS_BIN.md",
        (
            "test_check_suggestions_bin_status.py",
            "test_generate_suggestions_bin_report.py",
        ),
    ),
    (
        "docs/reports/suggestions_bin.json",
        (
            "test_check_suggestions_bin_status.py",
            "test_generate_suggestions_bin_report.py",
        ),
    ),
    (
        "docs/reports/dora_reliability_scoreboard",
        ("test_check_dora_reliability_scoreboard.py",),
    ),
    (
        "docs/reports/ruleset_drift_audit.json",
        ("test_check_merge_ruleset_deployment_guardrails.py",),
    ),
    (
        "docs/reports/reusable_workflow_inventory",
        ("test_generate_reusable_workflow_inventory.py",),
    ),
    (
        "docs/research/CAMPAIGN_WAVE_OPERATIONS_POLICY.md",
        ("test_check_campaign_wave_policy.py",),
    ),
    (
        "docs/research/templates/",
        ("test_check_campaign_wave_policy.py",),
    ),
    (
        "docs/research/templates/PRIVATE_WORKFLOW_SHARING_WARNING_CHECKLIST.md",
        ("test_check_reusable_workflow_governance_policy.py",),
    ),
    (
        "docs/research/OPENAI_ASYNC_EXECUTION_POLICY.md",
        ("test_check_openai_async_policy.py",),
    ),
    (
        "docs/research/JETSTREAM_OPENAI_CAMPAIGN_GUARDRAILS_POLICY.md",
        ("test_check_jetstream_openai_campaign_policy.py",),
    ),
    (
        "docs/research/WORKFLOW_CODEQL_MATRIX_GUARDRAILS_POLICY.md",
        ("test_check_workflow_codeql_matrix_policy.py",),
    ),
    (
        "docs/research/REUSABLE_WORKFLOW_GOVERNANCE_POLICY.md",
        ("test_check_reusable_workflow_governance_policy.py",),
    ),
    (
        "docs/research/JETSTREAM_CONSUMER_OPENAI_LOOP_POLICY.md",
        ("test_check_jetstream_consumer_openai_loop_policy.py",),
    ),
    (
        "docs/research/DEPENDENCY_REVIEW_SUPPLY_CHAIN_POLICY.md",
        ("test_check_dependency_review_policy.py",),
    ),
    (
        "docs/research/MERGE_RULESET_DEPLOYMENT_GUARDRAILS.md",
        ("test_check_merge_ruleset_deployment_guardrails.py",),
    ),
    (
        "docs/research/DEPENDENCY_INVENTORY_FORGE_GATES_POLICY.md",
        ("test_check_dependency_inventory_forge_policy.py",),
    ),
    (
        "docs/research/EVENT_RESILIENCE_AND_FLOW_CONTROL_POLICY.md",
        ("test_check_event_resilience_policy.py",),
    ),
    (
        "docs/research/ASYNC_EVAL_AND_HANDOFF_POLICY.md",
        ("test_check_async_eval_handoff_policy.py",),
    ),
    (
        "docs/research/RELEASE_AND_SUPPLY_CHAIN_POLICY.md",
        ("test_check_release_supply_chain_policy.py",),
    ),
    (
        "docs/research/CICD_TELEMETRY_ERROR_TAXONOMY_POLICY.md",
        ("test_check_cicd_telemetry_policy.py",),
    ),
    (
        "docs/research/WORKFLOW_OPERATOR_HANDOFF_RECOVERY_POLICY.md",
        ("test_check_workflow_operator_handoff_policy.py",),
    ),
    (
        "docs/research/WORKFLOW_HEALTH_BOARD.md",
        ("test_check_workflow_operator_handoff_policy.py",),
    ),
    (
        ".github/workflows/required-check-sentinel.yml",
        ("test_check_merge_queue_readiness.py",),
    ),
    (
        ".github/CODEOWNERS",
        ("test_check_merge_ruleset_deployment_guardrails.py",),
    ),
    (
        ".github/workflows/reusable-forge-gates.yml",
        (
            "test_check_dependency_inventory_forge_policy.py",
            "test_check_workflow_script_injection.py",
        ),
    ),
    (
        ".github/workflow-matrix-review-checklist.md",
        ("test_check_workflow_codeql_matrix_policy.py",),
    ),
    (
        "docs/research/templates/WORKFLOW_RUN_TRUST_BOUNDARY_CHECKLIST.md",
        ("test_check_workflow_codeql_matrix_policy.py",),
    ),
    (
        "docs/research/templates/JETSTREAM_CONSUMER_BASELINE_PROFILE_TEMPLATE.md",
        ("test_check_jetstream_consumer_openai_loop_policy.py",),
    ),
    (
        "docs/research/templates/OPENAI_PROMPT_OBJECT_REFERENCE_TEMPLATE.md",
        ("test_check_jetstream_consumer_openai_loop_policy.py",),
    ),
    (
        "docs/research/templates/OPENAI_COMPACTION_RESUME_PLAYBOOK_TEMPLATE.md",
        ("test_check_jetstream_consumer_openai_loop_policy.py",),
    ),
    (
        ".github/dependency-review-config.yml",
        ("test_check_dependency_review_policy.py",),
    ),
    (
        "docs/research/templates/OUTBOX_EVENT_RECORD_TEMPLATE.json",
        ("test_check_event_resilience_policy.py",),
    ),
    (
        "docs/research/templates/IDEMPOTENCY_LEDGER_ENTRY_TEMPLATE.json",
        ("test_check_event_resilience_policy.py",),
    ),
    (
        "docs/research/templates/AI_RMF_RISK_REGISTER_TEMPLATE.md",
        ("test_check_async_eval_handoff_policy.py",),
    ),
    (
        "docs/research/templates/DAEDALUS_DIAGRAM_TEMPLATE.md",
        ("test_check_async_eval_handoff_policy.py",),
    ),
    (
        "docs/research/templates/HERMES_RELAY_HANDOFF_TEMPLATE.md",
        ("test_check_async_eval_handoff_policy.py",),
    ),
    (
        "docs/research/templates/CICD_ERROR_TYPE_TAXONOMY_TEMPLATE.md",
        ("test_check_cicd_telemetry_policy.py",),
    ),
    (
        ".github/dependabot.yml",
        ("test_check_release_supply_chain_policy.py",),
    ),
    (
        "docs/WORKBENCH_LONG_TERM_ROADMAP.md",
        (
            "test_check_dora_reliability_scoreboard.py",
            "test_check_campaign_wave_policy.py",
            "test_check_openai_async_policy.py",
        ),
    ),
)


def _git_changed_files(base_ref: str | None) -> list[str]:
    if base_ref:
        cmd = ["git", "diff", "--name-only", f"{base_ref}...HEAD"]
    else:
        cmd = ["git", "status", "--porcelain"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return []

    lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if base_ref:
        return lines

    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        path = line[3:].strip()
        if path:
            paths.append(path)
    return paths


def _select_tests(changed_files: list[str], root: Path) -> list[str]:
    tests_root = root / "tests"
    all_tests = sorted(str(path) for path in tests_root.glob("test_*.py"))
    if not changed_files:
        return []

    changed_tokens = {Path(path).stem.lower() for path in changed_files}
    selected: set[str] = set()
    for test_path in all_tests:
        stem = Path(test_path).stem.lower().replace("test_", "")
        for token in changed_tokens:
            if token and (token in stem or stem in token):
                selected.add(test_path)

    # Explicit contract mappings for high-signal modules/docs.
    changed = set(changed_files)
    for prefix, test_names in EXPLICIT_TEST_MAPPINGS:
        if any(path.startswith(prefix) for path in changed):
            for test_name in test_names:
                selected.add(str(tests_root / test_name))

    return sorted(selected)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run pytest for changed-file impacts.")
    parser.add_argument(
        "--base-ref",
        default=None,
        help="Git base ref for diff selection (example: origin/main).",
    )
    parser.add_argument(
        "--fallback-all",
        action="store_true",
        help="Run full pytest when no mapped tests are found.",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    changed = _git_changed_files(args.base_ref)
    selected = _select_tests(changed, root)

    if selected:
        cmd = ["pytest", "-q", *selected]
    elif args.fallback_all:
        cmd = ["pytest", "-q"]
    else:
        print("No mapped tests for changed files.")
        return 0

    print(f"Running: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
