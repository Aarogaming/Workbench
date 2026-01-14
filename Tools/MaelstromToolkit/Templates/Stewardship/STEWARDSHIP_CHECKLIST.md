# Stewardship Checklist (Template)
- Controlled wait: do nothing unless feedback arrives.
- Log feedback verbatim (timestamp + source) in FEEDBACK_LOG.md.
- Classify: doc-only / cosmetic fix / out-of-scope.
- Cosmetic fixes: <=2 tiny commits, then re-freeze; no tab-order/behavior changes.
- Gates: dotnet build -c Debug; for UX changes, spot-check key screens at 175% DPI + narrow width.
- Tagging: new UX/tooling tags only when requested; never retag gold.
- Never refresh baselines or commit artifacts/ux/**.
