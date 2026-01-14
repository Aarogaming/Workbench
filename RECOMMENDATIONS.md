# AAS Shared Tools Recommendations

## Infrastructure & Standardization
1. **Unified Environment Discovery**: Create a `AuraSense.ps1` that centralizes the logic for finding `.venv`, `node_modules`, and `.dotnet` paths across all sibling repos.
2. **Global Configuration Manager**: Implement a `config_sync.ps1` to ensure `.env.example` files are consistent and help initialize local `.env` files from a central template.
3. **Cross-Repo Dependency Auditor**: Add a script to check for version mismatches in `requirements.txt`, `package.json`, and `build.gradle.kts` across the suite.
4. **Standardized Logging**: Create a shared logging wrapper for PowerShell scripts to ensure consistent output formatting and log rotation.

## Tooling Enhancements
5. **MyFortress CLI Implementation**: Replace the placeholder `hg_task.ps1` with a functional wrapper for the MyFortress `gateway/` logic.
6. **Android Build Automation**: Implement `android_task.ps1` with common Gradle tasks (build, lint, test) and emulator management.
7. **GUI Task Wrapper**: Define and implement `gui_task.ps1` to interface with the `HandoffTray` or `dashboard` components.
8. **Shared Git Hooks**: Create a `setup_hooks.ps1` to deploy pre-commit hooks (ruff, eslint, etc.) across all sibling repos.

## Developer Experience (DX)
9. **Interactive Hub Launcher**: Enhance `aas_hub.ps1` to support an interactive mode for selecting which service to launch.
10. **Unified Test Runner**: Expand `aas_tests.ps1` to include Android and MyFortress tests in a single summary report.
11. **Workspace Generator**: Create a script to generate/update the `.code-workspace` file to include all sibling directories dynamically.
12. **Documentation Aggregator**: Build a tool that scrapes `README.md` files from all sibling repos and generates a central `INDEX.md` in `Workbench`.

## Maintenance & Cleanup
13. **Venv Cleanup Utility**: Add a script to safely remove orphaned or outdated virtual environments across the `Dev library`.
14. **Artifact Purge**: Implement a global `ArcaneSweep.ps1` to clear `bin/`, `obj/`, `dist/`, `build/`, and `__pycache__` across all projects.
15. **License/Header Checker**: Ensure all source files across repos have consistent license headers.
16. **Secret Scanner**: Add a local tool to scan for accidentally committed secrets or hardcoded keys in the `Dev library`.

## Advanced Integration
17. **Maelstrom Integration**: Create a shared helper for `ProjectMaelstrom` tasks within the `Workbench` library.
18. **Docker Orchestrator**: Implement a `docker_manage.ps1` to coordinate `docker-compose` actions across AAS and MyFortress.
19. **CI/CD Local Simulator**: Create a script that runs the equivalent of `.gitlab-ci.yml` or `ci.yml` steps locally for validation.
20. **Shared Asset Manager**: A tool to sync or symlink common assets (icons, design tokens) from `Assets/` to specific project directories.
