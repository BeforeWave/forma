# Task Checklist

Replace this template with the final task checklist for the issue.

The finished `tasks.md` must contain only:

Task type is encoded inside `Accept:` for new tasks, preferably as `Task Type=<type>; ...`. Existing tasks without this marker default to `Task Type=step`. Supported types are `step`, `loop-batch`, `gate`, and `promote`.

- task headers in `- [ ] [<task-id>] ...` or `- [x] [<task-id>] ...` form
- exactly one `Accept:` line below each task
- one or more `Validate:` lines below each task
- optional repeated `Use-Check:` lines below each task
- optional repeated `Depends:` lines below each task, or exactly one `Depends: none`
- optional repeated `Constraint:` lines below each task

Do not keep this guidance in the final file.
Do not append tasks below the template text or example.

Example final file:

```text
- [ ] [update-target-flow] Implement the settled behavior change
Accept: Task Type=step; success path, invalid input path, and one regression check are covered
Validate: <project-native validation command>
Use-Check: fast-regression
Depends: prerequisite-review
Constraint: do not change out-of-scope behavior
```

`Depends:` lines must use bare task ids, for example `Depends: prerequisite-review`.
Use `Constraint:` for execution guardrails such as non-goals, touched-surface limits, or review gates; for `loop-batch`, include batch limits, selection rules, retry/skip rules, no-full-rerun guards, and write boundaries there. Do not repeat the task summary or `Accept:` line there.
Do not split a normal implementation task into separate "implement code" and "add tests" checklist items unless the test work is itself the standalone deliverable.
