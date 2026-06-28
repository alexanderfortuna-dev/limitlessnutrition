#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rehost_images.py — download every product's remote image into images/<code>.<ext>.

Reads products.json (field i = remote image URL, c = code) and mirrors each image
locally so the catalogue no longer depends on third-party hotlinks. Output feeds
clean_images.py, which produces the transparent packshots in images_clean/.

Idempotent: skips files that already exist. Safe to re-run after adding products.

Requires: requests  (pip install requests)
Usage:    python3 rehost_images.py
"""

import json
import os
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "images")
PRODUCTS = os.path.join(ROOT, "products.json")

EXT_BY_CT = {
    "image/jpeg": ".jpg", "image/jpg": ".jpg", "image/png": ".png",
    "image/webp": ".webp", "image/gif": ".gif",
}


def main():
    try:
        import requests
    except ImportError:
        raise SystemExit("Install dependency first:  pip install requests")

    os.makedirs(OUT, exist_ok=True)
    with open(PRODUCTS, encoding="utf-8") as f:
        products = json.load(f)

    ok = skip = fail = 0
    headers = {"User-Agent": "Mozilla/5.0 (LIMITLESS image rehost)"}
    for p in products:
        url, code = p.get("i", ""), p.get("c", "")
        if not url or not url.startswith("http") or not code:
            skip += 1
            continue
        # already downloaded?
        if any(os.path.exists(os.path.join(OUT, code + e)) for e in (".jpg", ".png", ".webp", ".gif")):
            skip += 1
            continue
        try:
            r = requests.get(url, headers=headers, timeout=20)
            r.raise_for_status()
            ext = EXT_BY_CT.get(r.headers.get("Content-Type", "").split(";")[0].strip(), ".jpg")
            with open(os.path.join(OUT, code + ext), "wb") as fo:
                fo.write(r.content)
            ok += 1
            if ok % 50 == 0:
                print(f"  ...{ok} downloaded")
            time.sleep(0.1)  # be polite to the source host
        except Exception as e:
            fail += 1
            print(f"  ! {code}: {e}")

    print(f"Done. downloaded={ok} skipped={skip} failed={fail} -> {os.path.relpath(OUT, ROOT)}/")


if __name__ == "__main__":
    main()
