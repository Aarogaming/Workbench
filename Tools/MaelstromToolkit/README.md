# MaelstromToolkit

Cross-platform .NET 8 CLI that codifies Aaroneous Automation Suite�s stewardship and UX discipline. Generates deterministic, safe scaffolds (docs/scripts/workflows/templates) without touching runtime code.

## Commands (Phase 1 scaffold)
- init --out <dir> [--force]: seed core docs (policy, tags, stewardship, UX maintenance)
- policy init --out <dir> [--force]: write POLICY_BOUNDARY.md + sample policy config
- tags init --out <dir> [--force]: write TAG_POLICY.md
- stewardship init --out <dir> [--force]: write STEWARDSHIP_CHECKLIST.md + FEEDBACK_LOG.md
- ux init --framework winforms|wpf|avalonia|winui --out <dir> [--force]: write UX maintenance/style/changelog/tokens templates
- ci add --provider github --profile tools-only --out <dir> [--force]: write path-filtered workflow template
- guild --out <dir> [--force]: placeholder for future Codex?ChatGPT bridge integration
- selftest: validate templates exist and dry-run generation (no overwrite unless --force)

## Safety
- Defaults to writing under --out; never overwrites existing files unless --force.
- Templates are deterministic and auditable; no network calls.
- Keep DevTools/tooling changes isolated from runtime.

## Template folder
- Templates/Policy, Templates/Tags, Templates/Stewardship, Templates/UX, Templates/CI, Templates/Guild

## Next steps
- Integrate full guild module (reuse GuildBridge logic) in a future phase.
- Expand profiles/templates as needed per framework.
