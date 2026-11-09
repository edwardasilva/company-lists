# company-lists

A plain list of companies by region: name, website, industry, field, city, state and a public source for each row. It starts with the Denver, Colorado metro. It lists companies only. It does not hold job postings.

[eeprep](https://github.com/edwardasilva/eeprep) includes this repo as a submodule at `data/company-lists`.

## Layout

| Path | What it is |
| --- | --- |
| `data/<country>/<state>/<region>.csv` | One file per metro region, such as `data/us/co/denver.csv` |
| `schema/company.schema.json` | The columns, their order, and the allowed values |
| `schema/industries.csv` | Every allowed `industry` and `field` pair |
| `scripts/validate.py` | Checks every data file. Python standard library only |

## Columns

Every file has the same header, in this order. An empty cell means unknown.

| Column | Required | Rule |
| --- | --- | --- |
| `id` | yes | Lowercase slug, unique across the whole repo. Never renamed or reused |
| `name` | yes | The company name as the company writes it |
| `website` | yes | Home page, `https://`, ending in `/`. One row per website in a file |
| `industry` | yes | An `industry` from `schema/industries.csv` |
| `field` | no | A `field` listed for that industry |
| `city` | yes | City of this location |
| `state` | yes | USPS code, and it matches the folder |
| `region` | yes | Metro name. Its slug is the file name, so `Denver` lives in `denver.csv` |
| `country` | yes | `US` for now, and it matches the folder |
| `hq` | yes | `true` when this location is the company headquarters |
| `size_band` | no | Employee band, such as `201-500`, only when a source states it |
| `ee_relevant` | no | `true` when the company hires electrical or computer engineers |
| `source_url` | yes | A public `https://` page that backs the row |
| `last_verified` | yes | The day someone checked the row against `source_url`, `YYYY-MM-DD` |
| `notes` | no | Short and neutral, 200 characters at most |

Rows are sorted by `id`. A company with sites in two regions gets a row in each file, with a different `id` such as `acme-denver`.

## Why CSV

One row per line keeps diffs small and reviewable, and GitHub shows each file as a table. Any spreadsheet, database or script reads it with no extra tools. Splitting by region keeps each file small as the list grows to thousands of rows, and two people adding different regions never touch the same file.

## Check the data

```bash
python3 scripts/validate.py
```

It checks the header, required cells, allowed values, URLs, unique ids, sorted order, duplicate websites, and that each row matches its folder and file name. It rejects email addresses and phone numbers. The Check workflow runs it on every pull request and on every push to `main`.

## Rules

- Never invent data. Every row cites a public page, and `last_verified` says when someone checked it.
- Public company information only. No personal names, emails, or phone numbers.
- Every change reaches `main` through a pull request, and every merge is a squash merge.

How to add rows is in [CONTRIBUTING](.github/CONTRIBUTING.md).

## License

The repo has two licenses, one for the dataset and one for code.

The dataset is licensed under [CC BY 4.0](LICENSE-CONTENT). You may share and adapt it if you give credit and link the license. The dataset means:

- the data files in `data/`
- the lists in `schema/`, including `schema/industries.csv` and the allowed values in `schema/company.schema.json`

Code is licensed under the [MIT License](LICENSE). Code means everything else, including the validator in `scripts/`, the workflows in `.github/`, and config files.

Company names and websites belong to their owners. Listing a company does not mean it endorses this project.
