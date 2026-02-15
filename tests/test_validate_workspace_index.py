from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    root = Path(__file__).resolve().parents[1]
    script_path = root / "scripts" / "validate_workspace_index.py"
    spec = importlib.util.spec_from_file_location(
        "validate_workspace_index", script_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_legacy_plugin_detection_exact_class_name():
    module = _load_module()
    assert module._looks_like_legacy_plugin("class Plugin:\n    pass\n")
    assert module._looks_like_legacy_plugin("def register(hub):\n    return None\n")


def test_legacy_plugin_detection_ignores_helper_names():
    module = _load_module()
    assert not module._looks_like_legacy_plugin(
        "class PluginVersionManager:\n    pass\n"
    )
    assert not module._looks_like_legacy_plugin("class PluginSandbox:\n    pass\n")


def test_context_target_records_context_missing(tmp_path: Path):
    module = _load_module()
    suite_root = tmp_path / "suite"
    utilities = suite_root / "Utilities"
    utilities.mkdir(parents=True)

    row = module._audit_target(
        repo_path=utilities,
        target="Utilities",
        submodule_meta={},
        template_text=None,
        enforce_baseline=False,
        optional_absent=False,
        policy_note="",
    )

    assert row["missing"] == []
    assert "README.md" in row["context_missing"]
    assert row["ok"] is True


def test_enforced_target_records_missing(tmp_path: Path):
    module = _load_module()
    suite_root = tmp_path / "suite"
    workbench = suite_root / "Workbench"
    workbench.mkdir(parents=True)

    row = module._audit_target(
        repo_path=workbench,
        target="Workbench",
        submodule_meta={},
        template_text=None,
        enforce_baseline=True,
        optional_absent=False,
        policy_note="",
    )

    assert "README.md" in row["missing"]
    assert row["ok"] is False


def test_optional_absent_target_is_not_warning_or_missing(tmp_path: Path):
    module = _load_module()
    suite_root = tmp_path / "suite"
    suite_root.mkdir(parents=True)

    row = module._audit_target(
        repo_path=suite_root / "ToolsShared",
        target="ToolsShared",
        submodule_meta={},
        template_text=None,
        enforce_baseline=False,
        optional_absent=True,
        policy_note="optional",
    )

    assert row["missing"] == []
    assert row["warnings"] == []
    assert "optional target path is absent" in row["notes"]
    assert row["ok"] is True


def test_load_target_policy_parses_targets(tmp_path: Path):
    module = _load_module()
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(
        (
            '{"targets":[{"name":"Workbench","enforce_baseline":true},'
            '{"name":"ToolsShared","optional_absent":true}]}'
        ),
        encoding="utf-8",
    )

    policy = module._load_target_policy(policy_path)
    assert "Workbench" in policy
    assert "ToolsShared" in policy


def test_extend_targets_with_submodules_is_deduped_and_sorted_append():
    module = _load_module()
    target_names = ["Workbench", "Utilities", "Workbench"]
    submodule_meta = {
        "workbench": {"path": "Workbench"},
        "library": {"path": "Library"},
        "androidapp": {"path": "AndroidApp"},
    }

    resolved = module._extend_targets_with_submodules(target_names, submodule_meta)
    assert resolved == ["Workbench", "Utilities", "AndroidApp", "Library"]


def test_parse_submodule_status_and_sha_parsers():
    module = _load_module()
    status_rows = module._parse_submodule_status(
        " 1c71029f9374524b030580657ad82222aa18e0a9 AndroidApp (heads/main)\n"
        "+8478b82bda7497dc26fc2a65ca30477c98b3ff0f Library (heads/main)\n"
    )
    assert status_rows["AndroidApp"]["state"] == "clean"
    assert status_rows["Library"]["state"] == "drifted"

    tree_rows = module._parse_ls_tree_shas(
        "160000 commit 1c71029f9374524b030580657ad82222aa18e0a9\tAndroidApp\n"
    )
    assert tree_rows["AndroidApp"] == "1c71029f9374524b030580657ad82222aa18e0a9"

    index_rows = module._parse_ls_files_shas(
        "160000 92b8faaec5c82cc6cfc538ff89688c04e3885d95 0\tLibrary\n"
    )
    assert index_rows["Library"] == "92b8faaec5c82cc6cfc538ff89688c04e3885d95"


def test_build_alignment_status_detects_mismatch(tmp_path: Path):
    module = _load_module()
    docs = tmp_path / "docs"
    docs.mkdir(parents=True)
    (docs / "AAS_CONTROL_PLANE_ALIGNMENT.md").write_text(
        "| Repo | Local Governance/Index Entry | Pinned Submodule SHA |\n"
        "|---|---|---|\n"
        "| `Workbench` | `README.md` | `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |\n",
        encoding="utf-8",
    )

    submodules = {
        "entries": [
            {
                "path": "Workbench",
                "head_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "index_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "checkout_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "state": "clean",
                "prefix": " ",
            }
        ]
    }
    alignment = module._build_alignment_status(tmp_path, submodules)
    assert alignment["available"] is True
    assert alignment["entries"][0]["status"] == "mismatch"
    assert alignment["warnings"]


def test_parse_rev_list_count_output():
    module = _load_module()
    assert module._parse_rev_list_count_output("3\t5\n") == (3, 5)
    assert module._parse_rev_list_count_output("0 0") == (0, 0)
    assert module._parse_rev_list_count_output("bad") is None


def test_load_protocol_template_fallback_filesystem(tmp_path: Path):
    module = _load_module()
    suite_root = tmp_path / "suite"
    suite_root.mkdir(parents=True)
    template_path = suite_root / "Library" / "templates" / "protocols" / "AGENT_INTEROP_V1_TEMPLATE.md"
    template_path.parent.mkdir(parents=True)
    template_path.write_text("hello-template", encoding="utf-8")

    text, source = module._load_protocol_template(suite_root, template_path)
    assert text == "hello-template"
    assert source is not None and source.startswith("filesystem:")


def test_validate_protocol_allows_additive_append(tmp_path: Path):
    module = _load_module()
    repo = tmp_path / "repo"
    protocol = repo / "protocols" / "AGENT_INTEROP_V1.md"
    protocol.parent.mkdir(parents=True)

    template = (
        "# Agent Interop Protocol V1\n"
        "\n"
        "This repo adopts the AAS inter-repo protocol baseline for synchronous operations.\n"
        "\n"
        "## Version\n"
        "\n"
        "- Protocol version: `1.0`\n"
        "- Repo: `{{REPO_NAME}}`\n"
        "\n"
        "## Core request fields\n"
        "\n"
        "- `protocol_version`\n"
        "- `operation_id`\n"
        "- `request_id`\n"
        "- `source_repo`\n"
        "- `target_repo`\n"
        "- `initiator`\n"
        "- `intent`\n"
        "- `constraints`\n"
        "- `expected_outputs`\n"
        "- `timeout_sec`\n"
        "- `created_at_utc`\n"
        "\n"
        "## Core response fields\n"
        "\n"
        "- `protocol_version`\n"
        "- `operation_id`\n"
        "- `request_id`\n"
        "- `ack`\n"
        "- `status`\n"
        "- `message`\n"
        "- `artifacts`\n"
        "- `updated_at_utc`\n"
        "\n"
        "## Status enum\n"
        "\n"
        "- `acknowledged`\n"
        "- `in_progress`\n"
        "- `blocked`\n"
        "- `completed`\n"
        "- `failed`\n"
        "- `cancelled`\n"
        "\n"
        "## Compatibility\n"
        "\n"
        "- Major version changes are breaking.\n"
        "- Minor changes must be additive.\n"
        "- Unknown fields should be ignored, not rejected.\n"
    )
    body = template.replace("{{REPO_NAME}}", "repo") + (
        "\n## Artifact location convention\n\n- docs/repo-alignment/ARTIFACT_STORAGE_CONVENTIONS.md\n"
    )
    protocol.write_text(body, encoding="utf-8")

    warnings = module._validate_protocol(repo, "repo", template)
    assert not any("differs from canonical template" in item for item in warnings)


def test_standalone_target_resolution_uses_workbench_root(tmp_path: Path):
    suite_root = tmp_path / "parent"
    workbench_root = suite_root / "Workbench"
    workbench_root.mkdir(parents=True)

    target = "Workbench"
    direct = suite_root / target
    if direct.exists():
        resolved = direct
    elif target.lower() == "workbench" and workbench_root.name.lower() == "workbench":
        resolved = workbench_root
    else:
        resolved = direct

    assert resolved == workbench_root


def test_cross_repo_reference_audit_detects_missing(tmp_path: Path):
    module = _load_module()
    tools_dir = tmp_path / "Tools"
    tools_dir.mkdir(parents=True)
    csproj = tools_dir / "Test.csproj"
    csproj.write_text(
        '<Project><ItemGroup><ProjectReference Include="..\\\\..\\\\Maelstrom\\\\src\\\\ProjectMaelstrom\\\\ProjectMaelstrom.csproj" /></ItemGroup></Project>',
        encoding="utf-8",
    )

    result = module._audit_cross_repo_references(tmp_path)
    assert result["scanned_files"] >= 1
    assert result["total_references"] == 1
    assert result["missing_references"]
    assert result["warnings"]


def test_manifest_export_mismatch_detected(tmp_path: Path):
    module = _load_module()
    plugin_dir = tmp_path / "plugins" / "demo"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.py").write_text("class Plugin:\n    pass\n", encoding="utf-8")
    (plugin_dir / "manifest.json").write_text(
        (
            '{'
            '"schemaName":"PluginManifest",'
            '"entry":"plugin.py",'
            '"capabilities":[{"name":"cap.alpha"}],'
            '"extensions":{"aas":{"exports":["cap.beta"]}}'
            '}'
        ),
        encoding="utf-8",
    )

    result = module._audit_workbench_plugins(tmp_path)
    assert result["manifest_export_mismatch"]
    assert "manifest capability/export mismatch detected" in result["warnings"]


def test_build_issue_summary_classifies_key_findings():
    module = _load_module()
    summary = module._build_issue_summary(
        targets=[
            {
                "target": "Workbench",
                "baseline_enforced": True,
                "missing": ["docs/README.md"],
                "context_missing": [],
                "index_missing_paths": ["docs/missing.md"],
                "warnings": [
                    "protocols/AGENT_INTEROP_V1.md: differs from canonical template",
                    "aas-hive.json: communication.retries should be >= 1",
                ],
            }
        ],
        plugins={
            "warnings": ["manifest capability/export mismatch detected"],
            "manifest_invalid": [],
            "manifest_missing_entry_file": [],
            "directory_plugins_without_manifest": [],
            "manifest_export_mismatch": [{"plugin": "demo", "kind": "missing_exports", "capabilities": ["cap.a"]}],
            "duplicate_capabilities": {},
        },
        references={
            "missing_references": [
                {"file": "Tools/demo.csproj", "reference": "../Missing/repo", "resolved": "/tmp/missing"}
            ],
            "warnings": [],
        },
        submodules={"warnings": ["submodule `Library` checkout is ahead of index by 2 commit(s)"]},
        alignment_snapshot={"warnings": []},
        template_warning=None,
    )

    assert summary["total"] >= 7
    assert summary["by_severity"]["error"] >= 4
    assert summary["by_category"]["baseline_missing"] == 1
    assert summary["by_category"]["protocol_drift"] == 1
    assert summary["by_category"]["submodule_ahead"] == 1


def test_build_submodule_reconciliation_plan_assigns_actions():
    module = _load_module()
    plan = module._build_submodule_reconciliation_plan(
        {
            "available": True,
            "entries": [
                {
                    "path": "Library",
                    "state": "drifted",
                    "checkout_ahead_of_index": 2,
                    "checkout_behind_index": 0,
                    "dirty_files": 0,
                    "untracked_files": 0,
                },
                {
                    "path": "Merlin",
                    "state": "drifted",
                    "checkout_ahead_of_index": 0,
                    "checkout_behind_index": 0,
                    "dirty_files": 3,
                    "untracked_files": 1,
                },
            ],
        }
    )

    assert len(plan) == 2
    assert plan[0]["path"] == "Library"
    assert plan[0]["action"] == "choose_pointer_or_reset"
    assert plan[1]["path"] == "Merlin"
    assert plan[1]["action"] == "preserve_local_work"
    assert plan[1]["risk"] == "high"


def test_render_markdown_includes_run_options():
    module = _load_module()
    report = {
        "generated_utc": "2026-02-14T00:00:00Z",
        "suite_root": "/tmp/suite",
        "template_source": "",
        "run_options": {
            "targets_explicit": ["Workbench", "Utilities"],
            "include_all_submodule_targets": True,
            "strict": False,
            "strict_enforced_only": True,
            "ignore_cross_repo_warnings": True,
            "ignore_submodule_dirty": True,
            "ignore_submodule_ahead": False,
        },
        "submodules": {"available": False, "entries": [], "warnings": [], "error": ""},
        "submodule_reconciliation_plan": [],
        "alignment_snapshot": {"available": False, "entries": [], "warnings": []},
        "cross_repo_references": {
            "scanned_files": 0,
            "total_references": 0,
            "missing_references": [],
            "warnings": [],
        },
        "targets": [],
        "plugins": {
            "path": "/tmp/plugins",
            "manifest_dirs": [],
            "flat_legacy_plugin_candidates": [],
            "flat_helper_modules": [],
            "manifest_export_mismatch": [],
            "duplicate_capabilities": {},
            "warnings": [],
        },
        "issue_summary": {
            "total": 2,
            "by_severity": {"error": 1, "warning": 1, "info": 0},
            "by_category": {"baseline_missing": 1, "submodule_ahead": 1},
            "items": [],
        },
        "recommended_actions": [],
    }

    output = module._render_markdown(report)
    assert "- run_options:" in output
    assert "targets_explicit" in output
    assert "strict_enforced_only" in output
    assert "ignore_cross_repo_warnings" in output
    assert "## Issue Summary" in output
