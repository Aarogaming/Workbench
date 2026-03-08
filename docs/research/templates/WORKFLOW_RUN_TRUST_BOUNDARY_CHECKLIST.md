# workflow_run Trust Boundary Checklist

Use this checklist whenever a workflow consumes artifacts from `workflow_run`.

- [ ] Treat all downloaded artifacts/workspace as untrusted until verification passes.
- [ ] Run provenance verification before executing artifact-derived content.
- [ ] Run digest verification before trusting artifact integrity.
- [ ] Record trust-boundary decision in run summary and operator handoff packet.
