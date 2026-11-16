# Contributing

Thanks for helping with the company list. Anyone can add or fix a company.

## Suggest a change

Open an [issue](https://github.com/edwardasilva/company-lists/issues/new/choose) and describe the change, such as which company, which city, and what is wrong or missing. A short description is all it needs.

## Add or fix a company

1. Fork the repo (or cut a short branch if you have write access).
2. Edit the state file, such as `data/us/colorado.csv`, and put the location's city in `city`. Each state has one file, and all 50 exist. A new state file goes at `data/us/<state>.csv`, named after the state, with the header of an existing file, and needs its row in `schema/states.csv`.
3. For each row, put a public page that states the company name and city in `source_url`, and set `last_verified` to today's date (`YYYY-MM-DD`).
4. Use an `industry` and `field` pair from `schema/industries.csv`. `careers_url` is optional. Use the company's own jobs page, not LinkedIn or another board.
5. Keep rows sorted by `id`.
6. If you can, run the check and fix anything it reports. If you skip it, maintainers run it before merging:

```bash
python3 scripts/validate.py
```

7. Open a pull request into `main` with a short description of what changed and why. That is all a pull request needs. An issue link is optional. Maintainers review the change, and each accepted change goes in as one squashed commit. The squashed commit names the repository owner as its only author, so leave `Co-authored-by` lines and other trailers out of your commit messages and the pull request description.

A finished row looks like this, in the column order of the file header. It is an example, not a real company:

```csv
example-co,Example Co,https://example.com/,,electronics,test-measurement,Denver,true,https://example.com/contact,2026-11-10,Headquarters on the contact page.
```

Write `notes` as one or two short phrases that say what the source shows or what the company makes. Start with a capital letter, join phrases with a semicolon, and end with a period.

## One row per company per city

A company gets one row for each city where it has a location, and never two rows for the same city in a state. Rows for the same company must have exactly the same `name` and `website`, so tools can merge them. The validator fails when a company repeats for the same city and state, or has a different `name` or `website` between its rows. Two rows are the same company when their website host or their name, ignoring case, matches.

## Coding agents

Use the `claude` label, or comment `@claude`, to hand an issue or pull request to the coding agent.

Only the repository owner can start the workflow. The owner may hand any issue to the coding agent, including one opened by someone outside the project, after reading it in full. The agent works on a branch and opens a pull request. It never pushes to `main`, merges, tags, or cuts a release.

## Which companies belong

A company belongs when a public page shows a location in the row's city where people do engineering work. A mailing address, an HR-only office, or a network point of presence is not enough. Universities and government labs count when they meet the same test.

## What belongs here

These rules apply to every row and every change.

- Public company facts only. No personal names, email addresses, or phone numbers, in any column. The validator rejects email addresses and phone numbers.
- Never invent data. Do not guess a company, a city, a website, a date or a size.
- Before you add or change a row, open its source and check that it says what the row says.
- Prefer the company's own website as `source_url`, and never cite a page behind a login or paywall.
- Leave an optional cell empty when no source states it.
- To add an `industry` or `field` value, change `schema/industries.csv` in the same pull request and say why.
- Never rename or reuse an `id`.
- No job postings yet.
- No emoji, and keep wording neutral.

A public source is a page anyone can open without logging in, such as a company About or Locations page.

## When a company changes

- Closed, or no longer has a location in that city: delete the row, and say why in the pull request.
- Acquired or renamed, and still has a location in that city: keep the row. Update `name`, `website` and `source_url`, keep the `id`, and add the old name to `notes`, such as "Formerly Acme."

## Releases

Only the repository owner cuts releases.

## Conduct

Be kind and assume good intent. To report a problem with someone's behavior, use GitHub's Report content feature or message the repository owner in private.

## License

By contributing, you agree that what you add, data and code alike, is licensed under the [MIT License](../LICENSE).
