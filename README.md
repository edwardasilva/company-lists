<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/brand/company-lists-lockup-dark-outlined.svg">
  <img src="docs/brand/company-lists-lockup-outlined.svg" alt="company-lists" width="320">
</picture>

# company-lists

A plain list of companies by region: name, website, industry, field, city, state and a public source for each row. It covers the Denver and Boulder metros in Colorado, the Austin and Houston metros in Texas, the Los Angeles and San Francisco Bay Area metros in California, and Northern Virginia, and it lists companies, not job postings.

[eeprep](https://github.com/edwardasilva/eeprep) includes this repo as a submodule at `company-lists`.

For students and new graduates looking for employers near them, starting with electrical and computer engineering.

Which companies belong is in [CONTRIBUTING](.github/CONTRIBUTING.md#which-companies-belong).

To report a wrong, closed, or missing company, [open an issue](https://github.com/edwardasilva/company-lists/issues) with the row's `id` and a public source.

AI tools were used to help build this list. Please check any row you rely on against its `source_url`, and send a fix when you find one.

## Layout

| Path | What it is |
| --- | --- |
| `data/<country>/<state>/<region>.csv` | One file per metro region, such as `data/us/co/denver.csv` |
| `schema/company.schema.json` | The columns, their order, and the allowed values |
| `schema/industries.csv` | Every allowed `industry` and `field` pair |
| `scripts/validate.py` | Checks every data file. Python standard library only |
| `scripts/check_links.py` | Opens every website and source_url and reports dead links and cross-domain redirects. Python standard library only |

Releases are git tags, such as `v0.1.0`. To depend on this data, pin a tag rather than `main`.

## Columns

Every file has the same header, in this order. An empty cell means unknown.

Files are UTF-8 without a byte order mark, with LF line endings and a final newline. Cells are comma separated, and a cell that contains a comma is wrapped in double quotes (RFC 4180). No cell contains a line break. `ee_relevant` holds `true` or `false`, or is empty.

| Column | Required | Rule |
| --- | --- | --- |
| `id` | yes | Lowercase slug, unique across the whole repo. Never renamed or reused |
| `name` | yes | The company name as the company writes it |
| `website` | yes | Home page, `https://`, ending in `/`. One row per company per region, with the same value in every region |
| `careers_url` | no | The company's own careers or jobs page, not a job board |
| `industry` | yes | An `industry` from `schema/industries.csv` |
| `field` | no | A `field` listed for that industry |
| `city` | yes | City of this location |
| `state` | yes | USPS code, and it matches the folder |
| `region` | yes | Metro name. Its slug is the file name, so `Denver` lives in `denver.csv` |
| `country` | yes | `US` for now, and it matches the folder |
| `size_band` | no | Employee band, such as `201-500`, only when a source states it |
| `ee_relevant` | no | `true` when the company's business is hardware, power, RF, embedded, controls, or software engineering, or a cited page shows such roles. Empty otherwise |
| `source_url` | yes | A public `https://` page that backs the row |
| `last_verified` | yes | The day the row was checked against `source_url`, `YYYY-MM-DD`, in UTC |
| `notes` | no | Short and neutral, 200 characters at most |

A region is a list of cities. `Boulder` covers Boulder, Broomfield, Lafayette, Longmont and Louisville. `Denver` covers the rest of the Denver metro, including Aurora, Brighton, Centennial, Denver, Edgewater, Englewood, Golden, Greenwood Village, Lakewood, Littleton, Lone Tree, Sedalia, Westminster and Wheat Ridge. `Austin` covers Austin and Round Rock. `Houston` covers Houston and Spring. `Los Angeles` covers Costa Mesa, El Segundo, Long Beach, Los Angeles, Pasadena, Redondo Beach and Rosemead. `San Francisco` covers Berkeley, Cupertino, Fremont, Livermore, Menlo Park, Mountain View, Oakland, San Jose, Santa Clara, Stanford and Sunnyvale. `Northern Virginia` covers Alexandria, Ashburn, Chantilly, Fairfax, Falls Church, Herndon, Manassas, McLean and Reston. To add a city, add it here in the same pull request as its first row.

Rows are sorted by `id`. A company with sites in more than one region gets a row in each file. An `id` may carry a region suffix, such as `acme-denver`. Use one when the company has, or may later have, rows in more than one region, and always use one when two rows would otherwise share an `id`. Some existing ids carry a suffix without a second row, and they stay as they are.

## Why CSV

One row per line keeps diffs small, and GitHub shows each file as a table. Splitting by region keeps each file small, and two people adding different regions never touch the same file.

## Check the data

```bash
python3 scripts/validate.py
```

It checks the header, required cells, allowed values, URLs, unique ids, sorted order, repeated companies (same name or website in a region, or the same city), a `name` or `website` that differs between regions, and that each row matches its folder and file name. It rejects email addresses and phone numbers. The Check workflow runs it on every pull request into `main`.

The Links workflow runs `python3 scripts/check_links.py` every Monday. It is not a required check. You can run it by hand with `python3 scripts/check_links.py` from the repo root.

## Rules

- Never invent data. Every row cites a public page, and `last_verified` says when the row was checked.
- Public company information only. No personal names, emails, or phone numbers.
- Every change reaches `main` through a pull request, and every merge is a squash merge.

How to add rows is in [CONTRIBUTING](.github/CONTRIBUTING.md).

## License

Everything in this repo is licensed under the [MIT License](LICENSE). That includes the data in `data/`, the files in `schema/`, and the scripts in `scripts/`.

Company names and websites belong to their owners. Listing a company does not mean it endorses this project.
