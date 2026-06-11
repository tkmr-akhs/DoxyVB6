# Domain Docs

Rules for engineering skills when reading domain documentation in this repository.

## Layout

Treat this repository as a single-context codebase.

- `CONTEXT.md`: domain glossary and assumptions for DoxyVB6 and ExcelModuleManager.
- `docs/adr/`: architecture decision records.

## Related Context

- Treat DoxyVB6 as an independent repository. Normal work should not assume the parent repository's domain documentation.
- The shared explanation of GitHub Issues, GitHub Projects, triage, and issue lifecycle lives in the parent repository `AGENTS.md`.
- For changes related to the Excel macro Doxygen-style comment rules, also check the parent repository `AGENTS.md` and the relevant Excel macro repository `CONTEXT.md`.

## Reading Rules

- Before starting domain-sensitive work, read the relevant `CONTEXT.md` and ADRs.
- If a file or ADR directory does not exist, do not treat that as a blocker. Continue with the available context.
- Prefer terms from `CONTEXT.md` in issues, design proposals, test names, and refactoring proposals.
- If a proposal conflicts with an existing ADR, identify the conflicting ADR explicitly.
- For conversion behavior, CLI behavior, or PowerShell wrapper changes, also check `README.md` and `example/`.
