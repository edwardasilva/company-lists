# Rules for agents

This repo is a public dataset of companies by region. Read `README.md` for the columns and `.github/CONTRIBUTING.md` for how a change lands.

## Git

- Work on a branch. Never push to `main`.
- Every change reaches `main` through a pull request, and every merge is a squash merge. Only Edward merges.
- The pull request body names its issue on its own line, as `Part of #N`. Add `Closes #N` when the pull request finishes the issue.
- Keep each pull request to one change, such as one region or one fix.
- Do not create tags. Do not force-push or rewrite pushed history.
- Releases stay on the 0.0.x line, and one is cut only when Edward says so.

## Data

- Never invent data. Do not guess a company, a city, a website, a date or a size.
- Every row needs a public `source_url` and a `last_verified` date. Open the source and check it says what the row says before you add or change the row.
- Prefer the company website as the source. Do not cite pages behind a login or paywall.
- Public company information only. No personal names, email addresses, or phone numbers, in any column.
- Leave an optional cell empty when no source states it.
- Use only `industry` and `field` values from `schema/industries.csv`. To add one, change that file in the same pull request and say why.
- Keep rows sorted by `id`. Never rename or reuse an `id`.
- No job postings yet.

## Checks

Run this before every push, and push only when it passes:

```bash
python3 scripts/validate.py
```

## Writing

- No emoji anywhere: files, commits, pull requests, comments, or output.
- Keep wording neutral and short. Examples use neutral names such as Alex Doe, with they and them.
- Never print or commit secrets, tokens, or environment variables.
