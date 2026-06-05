# Backend Rules

- Keep changes scoped to the backend behavior required by the current issue.
- Prefer fixing the root cause over masking symptoms.
- Call out API, schema, storage, queue, or deployment impact when relevant.
- Preserve backward compatibility unless the plan explicitly allows breaking changes.
- Avoid leaking sensitive data through logs, errors, or debug output.
- Consider rollback and operational failure modes for user-facing changes.
