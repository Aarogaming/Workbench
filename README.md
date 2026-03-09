# Workbench

Workbench is a utilities/tooling subproject in the Aaroneous Automation Suite (AAS)
ecosystem. It contains shared scripts and developer tools used across the workspace,
and is typically included as a git submodule.

## Canonical Docs

The canonical documentation lives in the AAS superproject:

- Start here: https://github.com/Aarogaming/AaroneousAutomationSuite/blob/master/docs/START_HERE.md
- Docs index: https://github.com/Aarogaming/AaroneousAutomationSuite/blob/master/docs/INDEX.md
- Gate governance pointer: `docs/GATE_GOVERNANCE_POINTER.md`

## Repo Map

- `Assets/`: Asset tooling (ingestion/index/search)
- `Tools/`: Developer tools
- `plugins/`: Workbench plugin modules

## Setup

```bash
git clone https://github.com/Aarogaming/Workbench.git
cd Workbench
cp .env.example .env
```

## Run

Use the AAS canonical docs and tooling entrypoints to run Workbench tasks for your current workflow.

## Test

Run repository tests and validation from your preferred CI-compatible runner.

