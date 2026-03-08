# Workflow Matrix Review Checklist

Use this checklist for any workflow introducing or modifying `strategy.matrix`.

## Default max-parallel by Workflow Class

- CI class default: max-parallel = 4
- Nightly class default: max-parallel = 2
- Policy class default: max-parallel = 1

## Matrix Declaration Checklist

- [ ] Workflow class documented (`ci`, `nightly`, `policy`)
- [ ] `max-parallel` declared explicitly
- [ ] `fail-fast` declared explicitly
- [ ] `continue-on-error` declared explicitly
- [ ] Deviation rationale documented in PR description/runbook
