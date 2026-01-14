# Tag Policy (Template)
- Gold tag (e.g., v1.0.0-gold): canonical baseline; immutable; never retag.
- UX tags (e.g., v1.x.y-ux): cosmetic-only checkpoints; no behavior/tab-order/policy/runtime changes.
- Tooling tags (e.g., v1.x.y-tools): DevTools-only; must pass selftest/CI; excluded from runtime packaging.
- Before tagging: run `dotnet build <solution> -c Debug`; if UX tag, spot-check primary screens at high DPI and narrow window width.
- Never refresh baselines or include artifacts/ux/** in tags.
