# Issue Tracker: GitHub

Issues and PRDs for this repository are managed in GitHub Issues. The target repository is `tkmr-akhs/DoxyVB6`.
When a mattpocock/skills workflow says to publish to the issue tracker, create a GitHub issue with the `gh` CLI.

## Language

Issue titles, issue bodies, PRDs, comments, labels created for DoxyVB6-specific workflow, and GitHub Projects text must be written in English.

## Repository

- GitHub remote: `https://github.com/tkmr-akhs/DoxyVB6.git`
- Run `gh` from this clone. Prefer `--repo tkmr-akhs/DoxyVB6` when issuing commands from outside the repository root.

## Conventions

- Create issue: `gh issue create --repo tkmr-akhs/DoxyVB6 --title "..." --body "..."`
- View issue: `gh issue view <number> --repo tkmr-akhs/DoxyVB6 --comments`
- List issues: `gh issue list --repo tkmr-akhs/DoxyVB6 --state open --json number,title,body,labels,comments`
- Add comment: `gh issue comment <number> --repo tkmr-akhs/DoxyVB6 --body "..."`
- Add label: `gh issue edit <number> --repo tkmr-akhs/DoxyVB6 --add-label "..."`
- Remove label: `gh issue edit <number> --repo tkmr-akhs/DoxyVB6 --remove-label "..."`
- Close issue: `gh issue close <number> --repo tkmr-akhs/DoxyVB6 --comment "..."`

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --repo tkmr-akhs/DoxyVB6 --comments`.

## GitHub Projects

Issues in this repository are managed with both GitHub Issues and GitHub Projects v2.
Use the `tkmr-akhs` user project #5, `DoxyVB6 main project`.
Use the `Status` project field and keep it aligned with the issue lifecycle described in the parent repository `AGENTS.md`.

| Issue state / label | Project `Status` | Agent action |
| --- | --- | --- |
| `ready-for-agent` | `Ready` | Mark the issue as ready for agent work. |
| Active implementation | `In progress` | Show that an agent is working on the issue. |
| Implementation complete + waiting for review + `ready-for-human` | `In review` | Mark the issue as ready for human review. |
| Review passed + acceptance criteria verified | `Done` | Remove `ready-for-human`, close the issue, and move the project item to `Done`. |

Rules:

- If an issue gets the `ready-for-agent` label, set project `Status` to `Ready`.
- When implementation starts, set project `Status` to `In progress`.
- When implementation is complete, remove `ready-for-agent`, add `ready-for-human`, and set project `Status` to `In review`.
- After review passes, verify acceptance criteria. If all pass, or if the maintainer explicitly declares unmet criteria out of scope, remove `ready-for-human`, close the issue, and set project `Status` to `Done`.
- Use `ready-for-human` to mean that a human can review the current state. Do not restrict it to implementation handoff only.
- If acceptance criteria remain unmet and the maintainer has not explicitly marked them out of scope, do not close the issue or move it to `Done`.
- Use `gh api graphql` for GitHub Projects v2 operations. If scope is missing, run `gh auth refresh -h github.com -s project` to add the Projects scope.
