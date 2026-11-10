# company-lists

A plain list of companies by region: name, website, industry, field, city, state and a public source for each row. It covers the Denver and Boulder metros in Colorado and the Austin and Houston metros in Texas, and it lists companies, not job postings.

[eeprep](https://github.com/edwardasilva/eeprep) includes this repo as a submodule at `company-lists`.

For students and new graduates looking for employers near them, starting with electrical and computer engineering.

To report a wrong, closed, or missing company, [open an issue](https://github.com/edwardasilva/company-lists/issues) with the row's `id` and a public source.

## Layout

| Path | What it is |
| --- | --- |
| `data/<country>/<state>/<region>.csv` | One file per metro region, such as `data/us/co/denver.csv` |
| `schema/company.schema.json` | The columns, their order, and the allowed values |
| `schema/industries.csv` | Every allowed `industry` and `field` pair |
| `scripts/validate.py` | Checks every data file. Python standard library only |

Releases are git tags, such as `v0.1.0`. To depend on this data, pin a tag rather than `main`.

## Columns

Every file has the same header, in this order. An empty cell means unknown.

Files are UTF-8 without a byte order mark, with LF line endings and a final newline. Cells are comma separated, and a cell that contains a comma is wrapped in double quotes (RFC 4180). No cell contains a line break. `hq` holds the text `true` or `false`. `ee_relevant` holds `true` or `false`, or is empty.

| Column | Required | Rule |
| --- | --- | --- |
| `id` | yes | Lowercase slug, unique across the whole repo. Never renamed or reused |
| `name` | yes | The company name as the company writes it |
| `website` | yes | Home page, `https://`, ending in `/`. One row per website in a file |
| `careers_url` | no | The company's own careers or jobs page, not a job board |
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
| `last_verified` | yes | The day someone checked the row against `source_url`, `YYYY-MM-DD`, in UTC |
| `notes` | no | Short and neutral, 200 characters at most |

Rows are sorted by `id`. A company with sites in more than one region gets a row in each file. An `id` gets a suffix, such as `acme-denver`, only when two rows would otherwise share one.

## Why CSV

One row per line keeps diffs small, and GitHub shows each file as a table. Splitting by region keeps each file small, and two people adding different regions never touch the same file.

## Check the data

```bash
python3 scripts/validate.py
```

It checks the header, required cells, allowed values, URLs, unique ids, sorted order, duplicate websites, and that each row matches its folder and file name. It rejects email addresses and phone numbers. The Check workflow runs it on every pull request into `main`.

## Rules

- Never invent data. Every row cites a public page, and `last_verified` says when someone checked it.
- Public company information only. No personal names, emails, or phone numbers.
- Every change reaches `main` through a pull request, and every merge is a squash merge.

How to add rows is in [CONTRIBUTING](.github/CONTRIBUTING.md).

## License

Everything in this repo is licensed under the [MIT License](LICENSE). That includes the data in `data/`, the files in `schema/`, and the scripts in `scripts/`.

Company names and websites belong to their owners. Listing a company does not mean it endorses this project.
