# Private Workflow Sharing Warning Checklist

Use before enabling private reusable workflow sharing across repositories.

## Risk Warnings

1. Logs from consumer workflow runs can expose behavior and metadata from shared private workflows.
2. `GITHUB_TOKEN` permissions remain scoped to the caller repository context.
3. Shared workflow maintainers must review token scope assumptions before rollout.

## Operator Confirmation

- [ ] Log visibility implications reviewed and accepted.
- [ ] Token scope expectations documented for caller and callee workflows.
- [ ] Repository allowlist for sharing boundary reviewed.
- [ ] Rollback path documented for emergency revocation.
