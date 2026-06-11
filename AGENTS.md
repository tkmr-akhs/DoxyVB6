# AGENTS.md

## Encoding and Line Endings

- All plain text files are UTF-8 without BOM, including `.md`, `.py`, `.ps1`, `.psm1`, `.psd1`, `.toml`, `.json`, `.bat`, `.spec`, and extensionless text files.
- Do not apply text encoding rules to binary files such as `.xlsm`, `.lnk`, `.exe`, `.png`, and `.jpg`.
- Use LF line endings for newly created or edited plain text files unless a tool-specific format requires otherwise.
- Plain text files should end with a trailing newline when they are created or edited.
- If `apply_patch` cannot safely preserve encoding or line endings, use PowerShell with `[System.IO.File]::ReadAllText` / `WriteAllText` and an explicit `[System.Text.UTF8Encoding]::new($false)`.

## Documentation Language Policy

- DoxyVB6 documentation is written in English.
- ADRs, `CONTEXT.md`, PRDs, issues, issue comments, GitHub Projects text, and agent-facing documentation must be written in English.
- Code identifiers must remain in English.
- Commit messages must follow Conventional Commits and must be written in English.
- Commit messages must use this structure: title, blank line, details, blank line, and optional footer.
  - Keep the details section to 200 characters or fewer.
  - TODO updates, unit test additions, and unit test results do not need to be mentioned.
  - For breaking API changes, write `BREAKING CHANGE:` in the footer or add `!` after the type/scope.

## Scope

This `AGENTS.md` applies only to the `DoxyVB6` repository. The parent `excel-macros-workspace` `AGENTS.md` contains development rules for the Excel macro repositories and does not apply directly to DoxyVB6.

The shared process explanation for GitHub Issues, GitHub Projects, triage labels, and issue lifecycle lives in the parent `excel-macros-workspace` `AGENTS.md`. DoxyVB6-specific tracker settings live in `docs/agents/issue-tracker.md`. DoxyVB6 tracker content is written in English.

DoxyVB6 is related to Excel/VBA documentation generation and Excel module import/export. When a change must stay compatible with Excel macro Doxygen-style comments or import/export workflows, also check the parent repository `AGENTS.md` and the relevant Excel macro repository `CONTEXT.md`.

## Agent Skills

When using mattpocock/skills, read DoxyVB6-specific context from this repository's documentation.

### GitHub Issues / Projects

For shared GitHub Issues, GitHub Projects, triage, and issue lifecycle process rules, refer to the parent `excel-macros-workspace` `AGENTS.md`. Apply DoxyVB6's English language policy to issue bodies, comments, PRDs, and project text.

For DoxyVB6-specific issue tracker details, refer to `docs/agents/issue-tracker.md`.

### Domain Documentation

Treat this repository as a single-context codebase. Before making domain-sensitive changes, check:

- `CONTEXT.md`: domain glossary and assumptions for DoxyVB6 and ExcelModuleManager.
- `docs/agents/domain.md`: reading rules for engineering skills.
- `docs/adr/`: architecture decision records. If the directory or relevant ADR does not exist, continue without treating it as a blocker.
- `README.md` and `example/`: behavior visible to users, CLI usage, PowerShell wrappers, and example workflows.

## Development and Verification

- For behavior changes in the Python package `src/DoxyVB6`, update `tests` and pin representative before/after conversion cases.
- For changes to the PowerShell module `src/ExcelModuleManager` or `.ps1` / `.bat` wrappers, consider Excel COM, VBIDE access, execution policy, and path resolution effects.
- Treat `build`, `dist`, `.venv`, and `.pytest_cache` as generated artifacts. Do not edit them directly during normal development.
- Keep `example` aligned with README behavior because it documents user-facing workflows.
- When changing Doxygen comment conversion behavior, verify that the change remains compatible with Doxygen-style comments used by the Excel macro repositories.
