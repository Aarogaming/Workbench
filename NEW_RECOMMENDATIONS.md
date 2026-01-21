# Additional AAS Shared Tools Recommendations (Based on Maelstrom/Merlin Context)

## Maelstrom & Bot Integration
21. **Maelstrom Bot Health Monitor**: Create `check_maelstrom_health.ps1` to probe `/healthz` and `/bot/api/status` across single/dual port modes.
22. **Job Queue Inspector**: Implement `get_maelstrom_jobs.ps1` to fetch and format the current job queue from `/bot/api/jobs`.
23. **Webhook Signature Validator**: A utility to test/validate HMAC signatures for GitHub and OpenAI webhooks locally.
24. **Maelstrom DB Reset Tool**: A safe script to reset the SQLite database (`maelstrombot.db`) and re-initialize the admin key as per the "Known Gotchas".
25. **Port Conflict Resolver**: A tool to scan for port conflicts (9410, 9411) and suggest/apply alternate ports in `.env`.

## Merlin & Merlin Integration
26. **Merlin Backend Launcher**: Implement `merlin_task.ps1` to launch the FastAPI backend and handle resource indexing.
27. **Merlin-AAS Context Syncer**: A script to automatically sync `Workbench` documentation and `INDEX.md` to Merlin's knowledge base.
28. **Chat History Backup**: Implement the Google Drive backup logic described in `MERLIN_GOOGLE_DRIVE_BACKUP.md` as a shared utility.
29. **Merlin Integration Tester**: A tool to verify Unity/Unreal/Electron client connectivity to the Merlin REST API.

## Advanced Automation & Safety
30. **Live Automation Guard**: A global check script that verifies `ALLOW_LIVE_AUTOMATION=false` across all project configs before allowing certain tasks.
31. **High-DPI UI Validator**: Implement a script to trigger `ui_check_regression.ps1` and capture screenshots at different scaling levels (100%, 125%, 150%).
32. **Guild Directory Watcher**: A background PowerShell job to monitor `artifacts/guild/to_hub/` and notify the user of new OpenAI requests.
33. **Resource-Aware Task Runner**: A wrapper that checks system resources (CPU/RAM) and game resources (energy/mana via OCR if available) before starting heavy tasks.
34. **Local LLM Bridge**: A tool to manage LM Studio model loading/unloading for parallel agent tasks.
35. **NEXUS Integration Auditor**: A script to verify cross-repo integration points defined in `NEXUS.md`.

## Developer Productivity (Dev-Side Tools)
36. **Global Git Status**: Create `GrimoireGit.ps1` to show the current branch, sync status, and dirty files for all sibling repos in a single view.
37. **Environment Doctor**: Implement `SpellCheck.ps1` to verify that all required runtimes (.NET 9, Python 3.12, Node 20, Java 17) are installed and in the PATH.
38. **Context Packager**: Create `export_context.ps1` to aggregate the structure and READMEs of all repos into a single "Context Pack" for AI assistants.
39. **Shared Script Scaffolder**: Implement `new_tool.ps1` to quickly generate new PowerShell tools with standard AAS imports and logging boilerplate.
40. **Unified Log Tailer**: A tool to tail logs from multiple projects (AAS, MyFortress, Merlin) simultaneously in one terminal window.

## Advanced Suite Coordination (Phase 4)
41. **Suite Port Mapper**: Create `ScryPortals.ps1` to list all ports used by the suite (9410, 9411, 8100, 5000, etc.) and verify their availability.
42. **Cross-Repo Search (Grep)**: Implement `SeekSpell.ps1` to perform high-speed regex searches across all sibling repos while ignoring build artifacts and venvs.
43. **Local LLM Health Check**: Create `check_llm.ps1` to verify if LM Studio is running and list currently loaded models.
44. **Profile Switcher**: Implement `switch_profile.ps1` to quickly swap between `dev`, `prod`, and `experimental` configuration profiles.
45. **AAS Agent Status**: Create `FamiliarCensus.ps1` to query the status of active agents in the AAS Hub.
46. **Dependency Graph Visualizer**: A tool to generate a Mermaid diagram of cross-repo dependencies.
47. **Vision Template Auditor**: A script to sync and verify OCR/ImageRec templates between Maelstrom and AAS.
48. **n8n Workflow Porter**: A utility to export/import n8n workflows between local and production instances.
49. **System Resource Dashboard**: A CLI dashboard showing resource consumption specifically for AAS suite processes.
50. **Automated Release Packager**: A tool to bundle project artifacts into versioned, portable ZIP files.
