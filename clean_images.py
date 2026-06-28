#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
clean_images.py — background-remove images/ into transparent images_clean/<code>.webp.

Uses rembg with the BiRefNet model for clean, studio-style cut-outs, then composites
onto a transparent canvas and saves as WebP. These are the assets index-clean.html
serves locally (no proxy), and the ones you upload to Hostinger public_html/images_clean/.

Idempotent: skips codes already present in images_clean/.

Requires: rembg, Pillow, onnxruntime  (pip install "rembg[cpu]" Pillow)
Usage:    python3 clean_images.py
"""

import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "images_clean")
MODEL = os.environ.get("REMBG_MODEL", "birefnet-general")


def main():
    try:
        from rembg import new_session, remove
        from PIL import Image
        import io
    except ImportError:
        raise SystemExit('Install dependencies first:  pip install "rembg[cpu]" Pillow')

    if not os.path.isdir(SRC):
        raise SystemExit(f"No source dir {SRC}/ — run rehost_images.py first.")

    os.makedirs(OUT, exist_ok=True)
    session = new_session(MODEL)

    files = [f for f in os.listdir(SRC) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
    ok = skip = fail = 0
    for fn in sorted(files):
        code = os.path.splitext(fn)[0]
        dest = os.path.join(OUT, code + ".webp")
        if os.path.exists(dest):
            skip += 1
            continue
        try:
            with open(os.path.join(SRC, fn), "rb") as f:
                cut = remove(f.read(), session=session)
            im = Image.open(io.BytesIO(cut)).convert("RGBA")
            # square, padded canvas keeps packshots visually consistent in the grid
            side = max(im.size)
            canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            canvas.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
            canvas.thumbnail((800, 800))
            canvas.save(dest, "WEBP", quality=85, method=6)
            ok += 1
            if ok % 50 == 0:
                print(f"  ...{ok} cleaned")
        except Exception as e:
            fail += 1
            print(f"  ! {code}: {e}")

    print(f"Done. cleaned={ok} skipped={skip} failed={fail} -> {os.path.relpath(OUT, ROOT)}/")


if __name__ == "__main__":
    main()
