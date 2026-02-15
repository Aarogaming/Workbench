# Workspace Index Audit

- generated_utc: `2026-02-14T03:19:11Z`
- suite_root: `/mnt/c/Dev library/AaroneousAutomationSuite`
- run_options:
  - targets_explicit: `-`
  - include_all_submodule_targets: `True`
  - strict: `False`
  - strict_enforced_only: `False`
  - ignore_submodule_dirty: `False`
  - ignore_submodule_ahead: `False`
- template_source: `pinned-submodule:Library@f2737f3202cad95e4ce546e24212ab0567193dcb:templates/protocols/AGENT_INTEROP_V1_TEMPLATE.md`

## Issue Summary

- total issues: `25`
- errors: `0`
- warnings: `25`
- info: `0`
- categories:
  - `submodule_ahead`: `6`
  - `submodule_checkout_state`: `6`
  - `submodule_dirty_worktree`: `6`
  - `submodule_pointer_mismatch`: `6`
  - `submodule_branch_divergence`: `1`

## Submodule Status

| Path | State | HEAD SHA | Index SHA | Checkout SHA | Ahead | Behind | Branch | Dirty | Untracked |
|---|---|---|---|---|---:|---:|---|---:|---:|
| `AndroidApp` | `drifted` | `1c71029f9374524b030580657ad82222aa18e0a9` | `1c71029f9374524b030580657ad82222aa18e0a9` | `4d0db0902cb12e3257cbe26eb4f0bbe627cca9ca` | 1 | 0 | `main...origin/main` | 20 | 4 |
| `Library` | `drifted` | `f2737f3202cad95e4ce546e24212ab0567193dcb` | `f2737f3202cad95e4ce546e24212ab0567193dcb` | `5727ba139bb6498db9f95c5ff4f25200ac798ba4` | 7 | 0 | `main...origin/main [ahead 7]` | 0 | 0 |
| `Maelstrom` | `drifted` | `b48008fca939792bf9591d063c972f0996f35cf0` | `b48008fca939792bf9591d063c972f0996f35cf0` | `fd2f0d92993b2f7f719a0f76776082d95453a4c2` | 1 | 0 | `main...origin/main` | 21 | 18 |
| `Merlin` | `drifted` | `50547c33d841d66cc048269df7a490db0eeae480` | `50547c33d841d66cc048269df7a490db0eeae480` | `407ab2e1dbdd8de4433f4e06ee10c2b0d0a5f43c` | 1 | 0 | `main...origin/main` | 32 | 89 |
| `MyFortress` | `drifted` | `a9c0d93706d2b1b478b7b9b3a9d518414d4b004e` | `a9c0d93706d2b1b478b7b9b3a9d518414d4b004e` | `a76b72af6a132b87ceb3440ab61175e2121a3cba` | 1 | 0 | `main...origin/main` | 15 | 5 |
| `Workbench` | `drifted` | `9f360a4ed49a3d6ed1878acc74e3cd989188f4ad` | `9f360a4ed49a3d6ed1878acc74e3cd989188f4ad` | `aaa947c74da18ba325b8cf4016e737797a792d7c` | 2 | 0 | `main...origin/main` | 50 | 7 |
| `guild` | `clean` | `b58d314fe65b713d7e5497fc382b853b5058afba` | `b58d314fe65b713d7e5497fc382b853b5058afba` | `b58d314fe65b713d7e5497fc382b853b5058afba` | 0 | 0 | `main...origin/main` | 0 | 2 |

- warnings:
  - submodule `AndroidApp` checkout state is `drifted` (4d0db0902cb12e3257cbe26eb4f0bbe627cca9ca)
  - submodule `AndroidApp` checkout SHA differs from index pointer (1c71029f9374524b030580657ad82222aa18e0a9 vs 4d0db0902cb12e3257cbe26eb4f0bbe627cca9ca)
  - submodule `AndroidApp` checkout is ahead of index by 1 commit(s)
  - submodule `AndroidApp` has local worktree changes (dirty=20 untracked=4)
  - submodule `Library` checkout state is `drifted` (5727ba139bb6498db9f95c5ff4f25200ac798ba4)
  - submodule `Library` checkout SHA differs from index pointer (f2737f3202cad95e4ce546e24212ab0567193dcb vs 5727ba139bb6498db9f95c5ff4f25200ac798ba4)
  - submodule `Library` checkout is ahead of index by 7 commit(s)
  - submodule `Library` branch divergence detected (main...origin/main [ahead 7])
  - submodule `Maelstrom` checkout state is `drifted` (fd2f0d92993b2f7f719a0f76776082d95453a4c2)
  - submodule `Maelstrom` checkout SHA differs from index pointer (b48008fca939792bf9591d063c972f0996f35cf0 vs fd2f0d92993b2f7f719a0f76776082d95453a4c2)
  - submodule `Maelstrom` checkout is ahead of index by 1 commit(s)
  - submodule `Maelstrom` has local worktree changes (dirty=21 untracked=18)
  - submodule `Merlin` checkout state is `drifted` (407ab2e1dbdd8de4433f4e06ee10c2b0d0a5f43c)
  - submodule `Merlin` checkout SHA differs from index pointer (50547c33d841d66cc048269df7a490db0eeae480 vs 407ab2e1dbdd8de4433f4e06ee10c2b0d0a5f43c)
  - submodule `Merlin` checkout is ahead of index by 1 commit(s)
  - submodule `Merlin` has local worktree changes (dirty=32 untracked=89)
  - submodule `MyFortress` checkout state is `drifted` (a76b72af6a132b87ceb3440ab61175e2121a3cba)
  - submodule `MyFortress` checkout SHA differs from index pointer (a9c0d93706d2b1b478b7b9b3a9d518414d4b004e vs a76b72af6a132b87ceb3440ab61175e2121a3cba)
  - submodule `MyFortress` checkout is ahead of index by 1 commit(s)
  - submodule `MyFortress` has local worktree changes (dirty=15 untracked=5)
  - submodule `Workbench` checkout state is `drifted` (aaa947c74da18ba325b8cf4016e737797a792d7c)
  - submodule `Workbench` checkout SHA differs from index pointer (9f360a4ed49a3d6ed1878acc74e3cd989188f4ad vs aaa947c74da18ba325b8cf4016e737797a792d7c)
  - submodule `Workbench` checkout is ahead of index by 2 commit(s)
  - submodule `Workbench` has local worktree changes (dirty=50 untracked=7)
  - submodule `guild` has local worktree changes (dirty=0 untracked=2)

## Submodule Reconciliation Plan

| Path | Risk | Ahead | Behind | Dirty | Untracked | Action | Command |
|---|---|---:|---:|---:|---:|---|---|
| `AndroidApp` | `high` | 1 | 0 | 20 | 4 | `preserve_local_work` | `git -C ../AndroidApp status --short --branch` |
| `Library` | `medium` | 7 | 0 | 0 | 0 | `choose_pointer_or_reset` | `git -C ../Library status --short --branch && git -C .. submodule update --init --recursive Library` |
| `Maelstrom` | `high` | 1 | 0 | 21 | 18 | `preserve_local_work` | `git -C ../Maelstrom status --short --branch` |
| `Merlin` | `high` | 1 | 0 | 32 | 89 | `preserve_local_work` | `git -C ../Merlin status --short --branch` |
| `MyFortress` | `high` | 1 | 0 | 15 | 5 | `preserve_local_work` | `git -C ../MyFortress status --short --branch` |
| `Workbench` | `high` | 2 | 0 | 50 | 7 | `preserve_local_work` | `git -C ../Workbench status --short --branch` |
| `guild` | `high` | 0 | 0 | 0 | 2 | `preserve_local_work` | `git -C ../guild status --short --branch` |

## Alignment Snapshot

| Repo | Docs Snapshot SHA | HEAD Pin SHA | Status |
|---|---|---|---|
| `AndroidApp` | `1c71029f9374524b030580657ad82222aa18e0a9` | `1c71029f9374524b030580657ad82222aa18e0a9` | `match` |
| `Library` | `f2737f3202cad95e4ce546e24212ab0567193dcb` | `f2737f3202cad95e4ce546e24212ab0567193dcb` | `match` |
| `Maelstrom` | `b48008fca939792bf9591d063c972f0996f35cf0` | `b48008fca939792bf9591d063c972f0996f35cf0` | `match` |
| `Merlin` | `50547c33d841d66cc048269df7a490db0eeae480` | `50547c33d841d66cc048269df7a490db0eeae480` | `match` |
| `MyFortress` | `a9c0d93706d2b1b478b7b9b3a9d518414d4b004e` | `a9c0d93706d2b1b478b7b9b3a9d518414d4b004e` | `match` |
| `Workbench` | `9f360a4ed49a3d6ed1878acc74e3cd989188f4ad` | `9f360a4ed49a3d6ed1878acc74e3cd989188f4ad` | `match` |

## Cross-Repo References

- scanned files: `43`
- total neighbor references: `4`
- missing references: none

## Neighbor Targets

| Target | Enforced | Exists | Submodule | Missing | Context Missing | Warnings |
|---|---|---|---|---:|---:|---:|
| Workbench | yes | yes | yes | 0 | 0 | 0 |
| Utilities | no | yes | no | 0 | 0 | 0 |
| ToolsShared | no | no | no | 0 | 0 | 0 |
| AndroidApp | yes | yes | yes | 0 | 0 | 0 |
| guild | yes | yes | yes | 0 | 0 | 0 |
| Library | yes | yes | yes | 0 | 0 | 0 |
| Maelstrom | yes | yes | yes | 0 | 0 | 0 |
| Merlin | yes | yes | yes | 0 | 0 | 0 |
| MyFortress | yes | yes | yes | 0 | 0 | 0 |

## Workbench Plugins

- plugin path: `/mnt/c/Dev library/AaroneousAutomationSuite/Workbench/plugins`
- manifest plugin dirs: `9`
- legacy flat plugin candidates: `0`
- flat helper modules: `34`
- manifest export mismatches: `0`
- duplicate capabilities: `0`
- warnings: none

## Detailed Findings

### Workbench

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/Workbench`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: `Primary managed module.`
- exists: `True`
- is_git_repo: `True`
- submodule_path: `Workbench`
- submodule_url: `https://github.com/Aarogaming/Workbench.git`
- missing: none
- warnings: none

### Utilities

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/Utilities`
- baseline_enforced: `False`
- optional_absent: `False`
- policy_note: `Neighboring context directory; not currently managed as an AAS module baseline.`
- exists: `True`
- is_git_repo: `False`
- submodule_path: `-`
- submodule_url: `-`
- missing: none
- warnings: none

### ToolsShared

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/ToolsShared`
- baseline_enforced: `False`
- optional_absent: `True`
- policy_note: `Legacy/optional neighbor path used for context discovery when present.`
- exists: `False`
- is_git_repo: `False`
- submodule_path: `-`
- submodule_url: `-`
- missing: none
- warnings: none
- notes:
  - optional target path is absent

### AndroidApp

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/AndroidApp`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: ``
- exists: `True`
- is_git_repo: `True`
- submodule_path: `AndroidApp`
- submodule_url: `https://github.com/Aarogaming/AndroidApp.git`
- missing: none
- warnings: none

### guild

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/guild`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: ``
- exists: `True`
- is_git_repo: `True`
- submodule_path: `guild`
- submodule_url: `https://github.com/Aarogaming/Guild.git`
- missing: none
- warnings: none

### Library

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/Library`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: ``
- exists: `True`
- is_git_repo: `True`
- submodule_path: `Library`
- submodule_url: `https://github.com/Aarogaming/Library.git`
- missing: none
- warnings: none

### Maelstrom

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/Maelstrom`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: ``
- exists: `True`
- is_git_repo: `True`
- submodule_path: `Maelstrom`
- submodule_url: `https://github.com/Aarogaming/Maelstrom.git`
- missing: none
- warnings: none

### Merlin

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/Merlin`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: ``
- exists: `True`
- is_git_repo: `True`
- submodule_path: `Merlin`
- submodule_url: `https://github.com/Aarogaming/Merlin.git`
- missing: none
- warnings: none

### MyFortress

- path: `/mnt/c/Dev library/AaroneousAutomationSuite/MyFortress`
- baseline_enforced: `True`
- optional_absent: `False`
- policy_note: ``
- exists: `True`
- is_git_repo: `True`
- submodule_path: `MyFortress`
- submodule_url: `https://github.com/Aarogaming/MyFortress.git`
- missing: none
- warnings: none

## Plugin File Lists

- manifest_dirs:
  - `asset_cleanup`
  - `asset_indexer`
  - `asset_search`
  - `asset_size_analysis`
  - `dpi_audit`
  - `kernel`
  - `license_consolidator`
  - `repo_compare`
  - `repo_size_guard`
- flat_legacy_plugin_candidates:
- flat_helper_modules:
  - `async_executor.py`
  - `build_cache_manager.py`
  - `context_summarization.py`
  - `custom_nodes.py`
  - `dancebot.py`
  - `datadog_validator.py`
  - `di_container.py`
  - `fuzz_testing.py`
  - `gradle_cache_manager.py`
  - `gui_cli_helper.py`
  - `gui_cli_wrapper.py`
  - `gui_hub_connector.py`
  - `gui_tray_status.py`
  - `home_assistant.py`
  - `https_release_enforcer.py`
  - `integration_engine.py`
  - `integration_tests.py`
  - `lint_baseline_manager.py`
  - `load_testing.py`
  - `log_export_manager.py`
  - `mcp_auth.py`
  - `multi_agent_conversations.py`
  - `periodic_check_workmanager.py`
  - `prompts.py`
  - `rbac.py`
  - `sandboxing.py`
  - `security_audit.py`
  - `settings_screen.py`
  - `status_history.py`
  - `url_edit_test_manager.py`
  - `versioning.py`
  - `versioning_strategy.py`
  - `voice.py`
  - `workflow_engine.py`
- manifest_export_mismatch:
- duplicate_capabilities:

## Recommended Actions

- Submodule pointer/checkout drift detected (AndroidApp, Library, Maelstrom, Merlin, MyFortress, Workbench); inspect with `git -C .. submodule status --recursive`, then reconcile via `git -C .. submodule update --init --recursive AndroidApp Library Maelstrom Merlin MyFortress Workbench` when ready.
- Submodule checkouts ahead of pinned pointer (AndroidApp, Library, Maelstrom, Merlin, MyFortress, Workbench); if intended, update superproject submodule pointer to include those commits.
- Drifted submodules have local edits (AndroidApp, Maelstrom, Merlin, MyFortress, Workbench); preserve work first (`git -C ../AndroidApp status --short --branch`) and commit/stash before running `git -C .. submodule update --init --recursive AndroidApp Library Maelstrom Merlin MyFortress Workbench`.
- Multiple submodules have local worktree churn (AndroidApp, Library, Maelstrom, Merlin, MyFortress, Workbench, guild); commit/stash/push as intended before treating workspace snapshots as a stable protocol baseline.
