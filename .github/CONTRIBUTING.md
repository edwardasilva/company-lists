# Contributing

This page covers how a company gets into the list.

## Start with an issue

Every change starts as a GitHub issue. Status lives on the project board, not in a comment thread.

## Add or change rows

1. Cut a short branch from `main`.
2. Edit the region file, such as `data/us/co/denver.csv`. For a new region, copy the header from an existing file into `data/<country>/<state>/<region>.csv`.
3. For each row, open a public page that states the company name and city, put it in `source_url`, and set `last_verified` to today.
4. Keep rows sorted by `id`.
5. Run `python3 scripts/validate.py` and fix anything it reports.
6. Open a pull request into `main`. Its body names the issue on its own line, as `Part of #12`.

Every merge is a squash merge, and the branch is deleted when it merges. Do not push straight to `main`.

## What belongs here

- Companies, with public facts from a public source. Never invent a row or a value.
- No personal contact details: no personal names, email addresses, or phone numbers. The validator rejects email addresses and phone numbers.
- No job postings yet.
- Optional cells stay empty unless a source states the value.

To add an `industry` or `field` value, add it to `schema/industries.csv` in sorted order in the same pull request, and say why.

## Working with Claude

Claude Code can take an issue to a pull request. `.github/workflows/claude.yml` runs it, and only the repo owner can start it, with the `claude` label or an `@claude` comment. Claude works on a `claude/` branch, runs the validator before it pushes, and never merges, pushes to `main`, tags, or cuts a release.

## Checks

The Check workflow runs `scripts/validate.py` on every pull request into `main` and on every push to `main`. The `protect-main` ruleset requires its `Validate data` job. Dependabot opens one grouped pull request a month for the workflow actions.

## License

By contributing, you agree that data you add is licensed under [CC BY 4.0](../LICENSE-CONTENT) and code under the [MIT License](../LICENSE). README has the split.
