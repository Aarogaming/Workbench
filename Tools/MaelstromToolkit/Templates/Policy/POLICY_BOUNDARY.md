# Policy Boundary (Template)
- Offline-first; live automation disabled by default.
- Capabilities gated by profile/policy; do not bypass policy checks.
- Executors must respect `ALLOW_LIVE_AUTOMATION=false` unless explicitly enabled in a controlled branch.
- No secrets embedded; use environment variables or local config ignored by VCS.
- Keep gold baseline immutable; policy changes require explicit approval and separate tagging.
