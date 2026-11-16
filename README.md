<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/brand/company-lists-lockup-dark-outlined.svg">
  <img src="docs/brand/company-lists-lockup-outlined.svg" alt="company-lists" width="320">
</picture>

A plain list of companies by US state, for students and new graduates looking for employers near them. It starts with electrical and computer engineering. There is one CSV file per state, and each row is one company in one city, with its name, website, industry, field and a public source. It lists companies, not job postings. As of v0.0.1 the 50 state files hold 1,993 rows, and Colorado has the most, with 152.

To use it, open the file for your state, such as `data/us/colorado.csv`. GitHub shows it as a table. The rules for which companies belong are in [CONTRIBUTING](.github/CONTRIBUTING.md#which-companies-belong). To report a wrong, closed, or missing company, [open an issue](https://github.com/edwardasilva/company-lists/issues) with the row's `id` and a public source. [eeprep](https://github.com/edwardasilva/eeprep) includes this repo as a submodule at `company-lists`.

AI tools helped build this list. `scripts/validate.py` checks every row against the schema, and `scripts/check_links.py` reports dead links, but neither checks that a source says what its row says. Check any row you rely on against its `source_url`, and send a fix if it is wrong.

## Layout

| Path | What it is |
| --- | --- |
| `data/us/<state>.csv` | One file per state, named after the state, such as `data/us/colorado.csv` |
| `schema/states.csv` | Every state file name, with its USPS code and state name |
| `schema/company.schema.json` | The columns, their order, and the allowed values |
| `schema/industries.csv` | Every allowed `industry` and `field` pair |
| `scripts/validate.py` | Checks every data file. Python standard library only |
| `scripts/check_links.py` | Opens every website and source_url and reports dead links and cross-domain redirects. Python standard library only |

Releases are git tags, such as `v0.0.1`. To depend on this data, pin a tag rather than `main`.

## Fetch the data

Every file has a stable raw address at a tag, so a script or a coding agent can read it without cloning the repo:

- One state: `https://raw.githubusercontent.com/edwardasilva/company-lists/v0.0.1/data/us/colorado.csv`
- The state files and their USPS codes: `https://raw.githubusercontent.com/edwardasilva/company-lists/v0.0.1/schema/states.csv`
- The columns: `https://raw.githubusercontent.com/edwardasilva/company-lists/v0.0.1/schema/company.schema.json`

`schema/company.schema.json` is a JSON Schema for one row. Its `x-columns` list gives the header in order, `x-nonempty` lists the cells that must not be empty, and each property gives the pattern or allowed values that `scripts/validate.py` checks. `schema/industries.csv` lists every allowed `industry` and `field` pair. Each row names the public page it comes from in `source_url` and the day it was checked in `last_verified`.

## Columns

Every file has the same header, in this order. An empty cell means unknown.

Files are UTF-8 without a byte order mark, with LF line endings and a final newline. Cells are comma separated, and a cell that contains a comma is wrapped in double quotes (RFC 4180). No cell contains a line break. `ee_relevant` holds `true`, or is empty.

| Column | Required | Rule |
| --- | --- | --- |
| `id` | yes | Lowercase slug, unique across the whole repo. Never renamed or reused |
| `name` | yes | The company name as the company writes it |
| `website` | yes | Home page, `https://`, ending in `/`. One row per company per city, with the same value in every row for that company |
| `careers_url` | no | The company's own careers or jobs page, not a job board |
| `industry` | yes | An `industry` from `schema/industries.csv` |
| `field` | no | A `field` listed for that industry |
| `city` | yes | City of this location. For a site on a military base, arsenal, test range or space center, use the installation name as the source gives it, with abbreviations spelled out, such as `Eglin Air Force Base`, not `Eglin AFB` |
| `ee_relevant` | no | `true` when the company's business is hardware, power, RF, embedded, controls, or software engineering, or a cited page shows such roles. Empty otherwise |
| `source_url` | yes | A public `https://` page that backs the row |
| `last_verified` | yes | The day the row was checked against `source_url`, `YYYY-MM-DD`, in UTC |
| `notes` | no | Short and neutral, 200 characters at most |

The country comes from the folder, and the state from the file name through `schema/states.csv`, so rows don't repeat them.

Each state has exactly one file, named after the state, such as `data/us/colorado.csv`. It covers every city in that state.

Rows are sorted by `id`. A company with sites in more than one city gets a row for each city. An `id` may carry a place suffix, such as `acme-denver` or `acme-co`. Use one when the company has, or may later have, more than one row, and always use one when two rows would otherwise share an `id`. Some existing ids carry a suffix without a second row, and they stay as they are.

## Why CSV

One row per line keeps diffs small, and GitHub shows each file as a table. Splitting by state keeps each file small, and two people adding different states never touch the same file.

## Check the data

```bash
python3 scripts/validate.py
```

It checks:

- the header
- required cells
- allowed values
- URLs
- unique ids
- sorted order
- repeated companies (same name or website for the same city and state)
- a `name` or `website` that differs between rows for the same company
- that each file path is `data/us/<state>.csv`, with its file name listed in `schema/states.csv`
- that `schema/states.csv` lists each file name and state code once

It rejects email addresses and phone numbers. The Check workflow runs it on every pull request into `main`.

The Links workflow runs `python3 scripts/check_links.py` every Monday. It is not a required check. You can run it by hand with `python3 scripts/check_links.py` from the repo root.

## Rules

Never invent data, and list only public company information. The full data rules are in [CONTRIBUTING](.github/CONTRIBUTING.md#what-belongs-here), with the steps to add a row. Every change reaches `main` through a pull request, and every merge is a squash merge.

## License

Everything in this repo is licensed under the [MIT License](LICENSE). That includes the data in `data/`, the files in `schema/`, and the scripts in `scripts/`.

Company names and websites belong to their owners. Listing a company does not mean it endorses this project.
