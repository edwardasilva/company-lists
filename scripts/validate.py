#!/usr/bin/env python3
"""Validate every CSV under data/ against schema/company.schema.json.

Standard library only. Usage:

    python3 scripts/validate.py            # check the whole repo
    python3 scripts/validate.py FILE ...   # check only these data files

Exits 1 and prints one line per problem when anything fails.
"""

import csv
import datetime
import io
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "schema" / "company.schema.json"
INDUSTRIES = ROOT / "schema" / "industries.csv"
DATA = ROOT / "data"
FORM = ROOT / ".github" / "ISSUE_TEMPLATE" / "company.yml"
# Folders use lowercase ISO country and USPS state codes. Rows no longer store them.
COUNTRIES = {"us"}
USPS = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL", "GA", "HI", "ID",
    "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO",
    "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA",
    "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "AS",
    "GU", "MP", "PR", "VI",
}

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
# North American numbers such as 303-555-0100, (303) 555 0100, +1 303.555.0100,
# and international numbers that start with +.
PHONE = re.compile(r"(\+?1[\s.-]?)?\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b|\+\d[\d\s().-]{7,}\d")
URL_FIELDS = ("website", "careers_url", "source_url")


def region_label(slug):
    return slug.replace("-", " ").title()


def load_schema():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    return schema["x-columns"], set(schema["x-nonempty"]), schema["properties"]


def load_industries():
    pairs = set()
    with INDUSTRIES.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            pairs.add((row["industry"], row["field"]))
    industries = {industry for industry, _ in pairs}
    return industries, pairs


def check_url(value):
    if any(c.isspace() for c in value):
        return "has whitespace"
    parts = urlsplit(value)
    if parts.scheme != "https":
        return "is not https"
    host = parts.hostname or ""
    if parts.username or parts.password:
        return "has a user or password"
    if parts.netloc != parts.netloc.lower():
        return "has an uppercase host"
    if "." not in host or host.startswith(".") or host.endswith("."):
        return "has no valid host"
    if re.fullmatch(r"[\d.]+", host):
        return "points at a local or IP host"
    return None


def site_key(url):
    host = (urlsplit(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def check_file(path, columns, nonempty, props, industries, pairs, seen_ids, today, catalog):
    problems = []
    rel = path.relative_to(ROOT).as_posix()

    def err(line, msg):
        problems.append(f"{rel}:{line}: {msg}")

    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        err(1, "starts with a byte order mark; save as UTF-8 without BOM")
    if b"\r" in raw:
        err(1, "has CR line endings; use LF")
    if raw and not raw.endswith(b"\n"):
        err(1, "does not end with a newline")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        err(1, f"is not UTF-8: {exc}")
        return problems, 0

    parts = path.relative_to(DATA).parts
    if len(parts) != 3 or not parts[2].endswith(".csv"):
        err(1, "must be data/<country>/<state>/<region>.csv")
        return problems, 0
    country_slug, state_slug, region_slug = parts[0], parts[1], parts[2][:-4]
    if country_slug not in COUNTRIES:
        err(1, f"country folder '{country_slug}' is not a supported lowercase country code")
        return problems, 0
    if state_slug != state_slug.lower() or state_slug.upper() not in USPS:
        err(1, f"state folder '{state_slug}' is not a lowercase USPS code")
        return problems, 0
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", region_slug):
        err(1, f"region file name '{parts[2]}' is not a lowercase slug")
        return problems, 0
    want_country, want_state, want_region = country_slug.upper(), state_slug.upper(), region_slug

    # newline="" leaves line splitting to the csv module, so only real line ends count.
    reader = csv.reader(io.StringIO(text, newline=""))
    header = next(reader, None)
    if header != columns:
        err(1, f"header must be exactly: {','.join(columns)}")
        return problems, 0

    prev_id = None
    rows = 0
    for cells in reader:
        line = reader.line_num
        rows += 1
        if len(cells) != len(columns):
            err(line, f"has {len(cells)} cells, expected {len(columns)}")
            continue
        row = dict(zip(columns, cells))

        for col, value in row.items():
            spec = props[col]
            if value != value.strip():
                err(line, f"{col} has leading or trailing spaces")
            if len(value.splitlines()) > 1:
                err(line, f"{col} has a line break")
            if col in nonempty and not value:
                err(line, f"{col} is empty")
                continue
            if not value and col not in nonempty:
                continue
            if "enum" in spec and value not in spec["enum"]:
                err(line, f"{col} '{value}' is not one of: {', '.join(v for v in spec['enum'] if v)}")
            if "pattern" in spec and not re.fullmatch(spec["pattern"], value):
                err(line, f"{col} '{value}' does not match {spec['pattern']}")
            if "maxLength" in spec and len(value) > spec["maxLength"]:
                err(line, f"{col} is longer than {spec['maxLength']} characters")
            if col not in URL_FIELDS and EMAIL.search(value):
                err(line, f"{col} contains an email address; personal contact details are not allowed")
            if col not in URL_FIELDS and PHONE.search(value):
                err(line, f"{col} contains a phone number; contact details are not allowed")

        for col in URL_FIELDS:
            if row[col]:
                why = check_url(row[col])
                if why:
                    err(line, f"{col} {why}")
                elif EMAIL.search(urlsplit(row[col]).path):
                    err(line, f"{col} contains an email address")

        rid = row["id"]
        if rid in seen_ids:
            err(line, f"id '{rid}' is already used at {seen_ids[rid]}")
        else:
            seen_ids[rid] = f"{rel}:{line}"
        if prev_id is not None and rid <= prev_id:
            err(line, f"rows must be sorted by id; '{rid}' comes after '{prev_id}'")
        prev_id = rid

        catalog.append((rel, line, row, (want_country, want_state, want_region)))

        if row["industry"] and row["industry"] not in industries:
            err(line, f"industry '{row['industry']}' is not in schema/industries.csv")
        elif row["field"] and (row["industry"], row["field"]) not in pairs:
            err(line, f"field '{row['field']}' is not listed for industry '{row['industry']}' in schema/industries.csv")

        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["last_verified"]):
            try:
                day = datetime.date.fromisoformat(row["last_verified"])
                if day > today:
                    err(line, f"last_verified {day} is in the future")
            except ValueError:
                err(line, f"last_verified {row['last_verified']} is not a real date")

    return problems, rows


def check_repeats(catalog):
    """Check repeated companies across all files.

    A company is the same when its website host or its lowercased name matches.
    Returns (files, message) pairs; the message starts with the first location.
    """
    found = []
    reported = set()
    groups = {}
    for entry in catalog:
        row = entry[2]
        if row["website"]:
            groups.setdefault(("website", site_key(row["website"])), []).append(entry)
        if row["name"]:
            groups.setdefault(("name", row["name"].lower()), []).append(entry)

    def add(a, b, kind, msg):
        pair = (a[:2], b[:2], kind)
        if pair in reported:
            return
        reported.add(pair)
        found.append(({a[0], b[0]}, f"{a[0]}:{a[1]}: {msg} (also {b[0]}:{b[1]})"))

    for (label, _), entries in sorted(groups.items()):
        for i, a in enumerate(entries):
            for b in entries[i + 1:]:
                ra, rb = a[2], b[2]
                loc_a, loc_b = a[3], b[3]
                if loc_a == loc_b:
                    add(a, b, "region", f"same company is listed twice in region {region_label(loc_a[2])} ({label} '{ra[label]}')")
                    continue
                if (ra["city"].lower(), loc_a[1]) == (rb["city"].lower(), loc_b[1]):
                    add(a, b, "city", f"same company is listed twice for {ra['city']}, {loc_a[1]} ({label} '{ra[label]}')")
                if ra["name"] != rb["name"]:
                    add(a, b, "name", f"name '{ra['name']}' must match '{rb['name']}' for the same company in another region")
                if ra["website"] != rb["website"]:
                    add(a, b, "website", f"website {ra['website']} must match {rb['website']} for the same company in another region")
    return found


def check_industries():
    problems = []
    with INDUSTRIES.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header != ["industry", "field", "label"]:
            return ["schema/industries.csv: header must be industry,field,label"]
        rows = list(reader)
    keys = [(r[0], r[1]) for r in rows if len(r) == 3]
    if len(keys) != len(rows):
        problems.append("schema/industries.csv: every row needs industry, field and label")
    if keys != sorted(keys):
        problems.append("schema/industries.csv: rows must be sorted by industry, then field")
    if len(set(keys)) != len(keys):
        problems.append("schema/industries.csv: has a duplicate industry and field pair")
    for industry, field in keys:
        for value in (industry, field):
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", value):
                problems.append(f"schema/industries.csv: '{value}' is not a lowercase slug")
    return problems


def form_options(text, field):
    """Return the dropdown options of one field in the issue form."""
    options, inside = [], False
    for line in text.split(f"    id: {field}\n", 1)[-1].splitlines():
        if line.startswith("  - type:"):
            break
        if inside and line.startswith("        - "):
            options.append(line[10:].strip().strip('"'))
        inside = inside or line.strip() == "options:"
    return options


def check_form(industries, props):
    """Check that every dropdown in the issue form is a schema column and offers the schema's values."""
    text = FORM.read_text(encoding="utf-8")
    problems = []
    want = {
        "industry": sorted(industries),
    }
    for field in re.findall(r"^  - type: dropdown\n    id: (\S+)$", text, re.M):
        if field not in props:
            problems.append(f".github/ISSUE_TEMPLATE/company.yml: dropdown {field} is not a column in schema/company.schema.json")
        elif "enum" in props[field]:
            # Not sure stands for an empty cell.
            want[field] = ["Not sure"] + [v for v in props[field]["enum"] if v]
    problems += [
        f".github/ISSUE_TEMPLATE/company.yml: {field} options must be: {', '.join(expected)}"
        for field, expected in want.items()
        if form_options(text, field) != expected
    ]
    return problems


def main(argv):
    columns, nonempty, props = load_schema()
    industries, pairs = load_industries()
    problems = check_industries()
    problems += check_form(industries, props)
    # Ids are unique across the repo, so every file is read even when only some are named.
    files = sorted(DATA.rglob("*.csv"))
    named = {Path(a).resolve() for a in argv}
    for p in sorted(named - {f.resolve() for f in files}):
        problems.append(f"{p}: not a data file under data/")
    stray = [p for p in DATA.rglob("*") if p.is_file() and p.suffix != ".csv" and p.name != ".gitkeep"]
    for p in stray:
        problems.append(f"{p.relative_to(ROOT).as_posix()}: only .csv files belong under data/")
    seen_ids = {}
    today = datetime.date.today() + datetime.timedelta(days=1)  # allow for time zones
    rows = 0
    catalog = []
    for path in files:
        found, count = check_file(path, columns, nonempty, props, industries, pairs, seen_ids, today, catalog)
        if not named or path.resolve() in named:
            problems.extend(found)
        rows += count
    named_rel = {p.relative_to(ROOT).as_posix() for p in named if p.is_relative_to(ROOT)}
    for rels, msg in check_repeats(catalog):
        if not named or rels & named_rel:
            problems.append(msg)

    if problems:
        for problem in problems:
            print(f"::error::{problem}" if "GITHUB_ACTIONS" in os.environ else problem)
        print(f"[ERROR] {len(problems)} problem(s) in {len(files)} file(s).")
        return 1
    checked = len([p for p in files if not named or p.resolve() in named])
    print(f"[SUCCESS] {checked} file(s), {rows} row(s), {len(pairs)} industry fields. All valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
