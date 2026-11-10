#!/usr/bin/env python3
"""Open every website and source_url in data/ and report the ones to fix.

Standard library only. Usage:

    python3 scripts/check_links.py

Fails on a page that is gone and on a website that redirects to another domain,
which usually means a rebrand, an acquisition or a closure. Exits 1 when any
link needs a fix.
"""

import csv
import glob
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
# Bot walls (Cloudflare, sec.gov, fcc.gov) answer a script with these codes while the
# page opens in a browser. A timeout or a 5xx is often the same thing. They warn so a
# person can look, and they never fail the check.
SOFT = {401, 403, 405, 406, 429, 999}


def site(url):
    # The last two labels of the host. Close enough while every row is a US company.
    return ".".join((urlsplit(url).hostname or "").lower().split(".")[-2:])


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, e.geturl()
    except Exception as e:
        return None, f"{type(e).__name__}: {getattr(e, 'reason', e)}"


def main():
    jobs = []
    for path in sorted(glob.glob("data/*/*/*.csv")):
        with open(path, encoding="utf-8", newline="") as f:
            for line, row in enumerate(csv.DictReader(f), start=2):
                for col in ("website", "source_url"):
                    jobs.append((path, line, row["id"], col, row[col]))
    bad = 0
    with ThreadPoolExecutor(8) as pool:
        results = pool.map(lambda job: fetch(job[4]), jobs)
        for (path, line, rid, col, url), (code, final) in zip(jobs, results):
            where = f"{path}:{line}: {rid} {col} {url}"
            if code is None or code in SOFT or code >= 500:
                print(f"::warning::{where} could not be checked ({code or final})")
            elif code >= 400:
                bad += 1
                print(f"::error::{where} answers HTTP {code}")
            elif col == "website" and site(final) != site(url):
                bad += 1
                print(
                    f"::error::{where} redirects to another site, {final}. "
                    "Check for a rebrand, an acquisition or a closure."
                )
    print(f"{len(jobs)} links checked, {bad} to fix.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
