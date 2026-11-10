#!/usr/bin/env python3
"""Validate every CSV under data/ against schema/company.schema.json.

Standard library only. Usage:

    python3 scripts/validate.py            # check the whole repo
    python3 scripts/validate.py FILE ...   # check only these data files

Exits 1 and prints one line per problem when anything fails.
"""

import csv
import datetime
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

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
# North American numbers such as 303-555-0100, (303) 555 0100, +1 303.555.0100,
# and international numbers that start with +.
PHONE = re.compile(r"(\+?1[\s.-]?)?\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b|\+\d[\d\s().-]{7,}\d")
URL_FIELDS = ("website", "source_url")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


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
    if "." not in host or host.startswith(".") or host.endswith("."):
        return "has no valid host"
    if host in ("localhost",) or re.fullmatch(r"[\d.]+", host):
        return "points at a local or IP host"
    return None


def site_key(url):
    host = (urlsplit(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def check_file(path, columns, nonempty, props, industries, pairs, seen_ids, today):
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
        return problems

    parts = path.relative_to(DATA).parts
    if len(parts) != 3 or not parts[2].endswith(".csv"):
        err(1, "must be data/<country>/<state>/<region>.csv")
        return problems
    want_country, want_state, want_region = parts[0].upper(), parts[1].upper(), parts[2][:-4]

    reader = csv.reader(text.splitlines())
    header = next(reader, None)
    if header != columns:
        err(1, f"header must be exactly: {','.join(columns)}")
        return problems

    prev_id = None
    sites = {}
    for line, cells in enumerate(reader, start=2):
        if len(cells) != len(columns):
            err(line, f"has {len(cells)} cells, expected {len(columns)}")
            continue
        row = dict(zip(columns, cells))

        for col, value in row.items():
            spec = props[col]
            if value != value.strip():
                err(line, f"{col} has leading or trailing spaces")
            if "\n" in value:
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

        if row["website"]:
            key = site_key(row["website"])
            if key in sites:
                err(line, f"website {row['website']} duplicates line {sites[key]}")
            else:
                sites[key] = line

        if row["industry"] and row["industry"] not in industries:
            err(line, f"industry '{row['industry']}' is not in schema/industries.csv")
        elif row["field"] and (row["industry"], row["field"]) not in pairs:
            err(line, f"field '{row['field']}' is not listed for industry '{row['industry']}' in schema/industries.csv")

        if row["country"] and row["country"] != want_country:
            err(line, f"country {row['country']} does not match the folder {parts[0]}")
        if row["state"] and row["state"] != want_state:
            err(line, f"state {row['state']} does not match the folder {parts[1]}")
        if row["region"] and slug(row["region"]) != want_region:
            err(line, f"region '{row['region']}' does not match the file name {parts[2]}")

        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["last_verified"]):
            try:
                day = datetime.date.fromisoformat(row["last_verified"])
                if day > today:
                    err(line, f"last_verified {day} is in the future")
            except ValueError:
                err(line, f"last_verified {row['last_verified']} is not a real date")

    return problems


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


def main(argv):
    columns, nonempty, props = load_schema()
    industries, pairs = load_industries()
    problems = check_industries()
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
    for path in files:
        found = check_file(path, columns, nonempty, props, industries, pairs, seen_ids, today)
        if not named or path.resolve() in named:
            problems.extend(found)
        rows += max(0, sum(1 for _ in path.open(encoding="utf-8", errors="replace")) - 1)

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
