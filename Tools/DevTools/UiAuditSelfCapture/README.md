# UiAuditSelfCapture (Dev-only)

Generates a full UI audit pack without changing Windows DPI or using UIA navigation. It instantiates the WinForms screens, applies simulated scale factors (100/125/150/175), captures PNGs, writes a README, and zips everything to `ui-audit/ui_audit_pack_selfcapture.zip` (default output).

## How to run (one command)

```powershell
dotnet run --project DevTools/UiAuditSelfCapture/UiAuditSelfCapture.csproj -- DevTools/UiAuditSelfCapture/ui_self_capture_config.json
```

If `ui_self_capture_config.json` is missing, the tool will create one using the sample defaults (output to `ui_audit_pack`, scales 1.0/1.25/1.5/1.75).
The bundled config writes to `ui-audit/ui_audit_pack_selfcapture`.

## Output
- `ui-audit/ui_audit_pack_selfcapture/` containing PNGs for:
  - Main
  - Plugins
  - Policy snapshot
  - Overlay preview
  - Manage Scripts
  - GitHub install area
- `README.txt` inside the output directory with status per capture
- `ui_audit_pack_selfcapture.zip` alongside the output folder

## Notes
- Dev-only tool; excluded from portable builds.
- No UI Automation or OS input; uses WinForms rendering (`DrawToBitmap`).
- If a screen cannot be captured, it is recorded as missing in the README and the tool continues.
