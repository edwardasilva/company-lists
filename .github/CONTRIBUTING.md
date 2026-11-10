# Contributing

Thanks for helping with the company list. Anyone can add or fix a company.

## Suggest a change

Open an [issue](https://github.com/edwardasilva/company-lists/issues/new/choose) and pick a template. Say which company, which metro, and what is wrong or missing.

## Add or fix a company

1. Fork the repo (or cut a short branch if you have write access).
2. Edit the metro file, such as `data/us/co/denver.csv`. For a new metro, copy the header from an existing file into `data/<country>/<state>/<region>.csv`.
3. For each row, put a public page that states the company name and city in `source_url`, and set `last_verified` to today's date (`YYYY-MM-DD`).
4. Use an `industry` and `field` pair from `schema/industries.csv`. Leave `size_band` empty unless a cited page gives a headcount. `careers_url` is optional. Use the company's own jobs page, not LinkedIn or another board.
5. Keep rows sorted by `id`.
6. Run the check and fix anything it reports:

```bash
python3 scripts/validate.py
```

7. Open a pull request into `main`.

A finished row looks like this, in the column order of the file header. It is an example, not a real company:

```csv
example-co,Example Co,https://example.com/,,electronics,test-measurement,Denver,CO,Denver,US,true,,true,https://example.com/contact,2026-11-10,Headquarters on the contact page.
```

Write `notes` as one or two short phrases that say what the source shows or what the company makes. Start with a capital letter, join phrases with a semicolon, and end with a period.

## Coding agents

Use the `gemini` label, or comment `@gemini-cli`, for easy tasks: low severity, small, one or two files, docs, wording, config, tests, or polish.

Use the `claude` label, or comment `@claude`, for harder work: medium or high severity, multi-file changes, design, security, workflows, or anything that needs judgment.

Only the repository owner can start either workflow. Both work on a branch and open a pull request. Neither pushes to `main`, merges, tags, or cuts a release.

## What belongs here

Public company facts only. Never invent a row. No personal names, emails, or phone numbers. The validator rejects emails and phone numbers. No job postings yet. Prefer the company's own website as `source_url`, and never cite a page behind a login or paywall. Never rename or reuse an `id`. No emoji, and keep wording neutral.

A public source is a page anyone can open without logging in, such as a company About or Locations page.

## Releases

Before cutting a release, run release-cut and land or close every `release-sweep` issue.

## Conduct

Be kind and assume good intent. To report a problem with someone's behavior, use GitHub's Report content feature or message the repository owner in private.

## License

By contributing, you agree that what you add, data and code alike, is licensed under the [MIT License](../LICENSE).
