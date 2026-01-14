# Contributing

Thank you for your interest in contributing to Workbench!

## Before you start
- Check for open issues or discussions in the repository.
- Propose significant changes via an issue before submitting a PR.
- Do not commit secrets or credentials.

## Development setup
- Install dependencies as required by each script (see script headers or `py-env.md`/`dotnet-env.md`).
- Lint Python: `flake8 .`
- Format Python: `black .`
- Test: Add and run tests where applicable.

## Branching and commits
- Branch naming: `feature/<short-description>`, `bugfix/<short-description>`
- Commit message style: Use imperative mood (e.g., "Add asset ingestion tool")
- PRs should include: summary, testing notes, screenshots (if UI)

## Code style
- Follow language-specific best practices and the repo's `.editorconfig` rules.
- Document public interfaces and modules.
- Add or update tests for new or changed behavior.

## Reporting issues
Include:
- Steps to reproduce
- Expected vs actual behavior
- Logs or screenshots if relevant

## Security
If you find a security issue, do not open a public issue. Contact the maintainer directly.
