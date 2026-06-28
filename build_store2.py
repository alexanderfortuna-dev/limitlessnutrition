#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_store2.py — LIMITLESS static storefront generator (Archetype A).

Reads products.json (list of {c,t,k,i,q,price?,compareAt?}) and cats.json,
injects the data into ONE self-contained HTML template, and writes TWO outputs:

    index.html        -> remote images via weserv proxy (Hostinger-friendly, no local assets)
    index-clean.html  -> local images_clean/<code>.webp (rembg/BiRefNet cut-outs)

Both share the exact same template; only the CLEAN_BUILD flag differs, so the
img() fallback chain (local -> proxy -> procedural SVG packshot) stays intact.

If products.json is missing, a realistic demo dataset is generated and written
so the store builds out-of-the-box. Replace products.json + cats.json with your
real export (2,523 products) and re-run — nothing else changes.

Usage:
    python3 build_store2.py
"""

import json
import os
import random

ROOT = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_JSON = os.path.join(ROOT, "products.json")
CATS_JSON = os.path.join(ROOT, "cats.json")
OUT_PROXY = os.path.join(ROOT, "index.html")
OUT_CLEAN = os.path.join(ROOT, "index-clean.html")

# --------------------------------------------------------------------------- #
#  Demo data generation (used only when products.json is absent)
# --------------------------------------------------------------------------- #

DEMO_CATS = [
    {"k": "whey",      "n": "Whey Protein",        "g": "massa"},
    {"k": "gainer",    "n": "Mass Gainer",         "g": "massa"},
    {"k": "preworkout","n": "Pre-Workout",         "g": "performa"},
    {"k": "amino",     "n": "BCAA & Asam Amino",   "g": "pemulihan"},
    {"k": "creatine",  "n": "Creatine",            "g": "performa"},
    {"k": "vitamin",   "n": "Vitamin & Mineral",   "g": "kesehatan"},
    {"k": "fatburner", "n": "Fat Burner",          "g": "diet"},
    {"k": "bar",       "n": "Protein Bar & Snack", "g": "diet"},
    {"k": "joint",     "n": "Kesehatan Sendi",     "g": "kesehatan"},
    {"k": "omega",     "n": "Omega & Fish Oil",    "g": "kesehatan"},
    {"k": "gear",      "n": "Aksesoris Gym",       "g": "performa"},
    {"k": "isotonik",  "n": "Minuman Isotonik",    "g": "performa"},
]

DEMO_BRANDS = [
    "Optimum Nutrition", "Dymatize", "MuscleTech", "BSN", "Rule One",
    "Evogen", "Kaged", "Applied Nutrition", "Nutrex", "Ultimate Nutrition",
    "Myprotein", "Isopure", "Allmax", "Cellucor",
]

DEMO_TYPE = {
    "whey":      ["Gold Standard 100% Whey", "ISO 100 Hydrolyzed", "Nitro-Tech Whey", "Syntha-6 Whey", "R1 Whey Blend"],
    "gainer":    ["Serious Mass", "Super Mass Gainer", "Mass-Tech Extreme", "True-Mass 1200", "R1 Mass Gainer"],
    "preworkout":["Gold Pre", "C4 Original", "Pre JYM", "Total War", "NeuroCore"],
    "amino":     ["Amino Energy", "BCAA 2:1:1", "Xtend BCAA", "EAA Max", "Intra-Aid"],
    "creatine":  ["Micronized Creatine", "Creatine HCL", "Creapure Mono", "Kre-Alkalyn", "Creatine Caps"],
    "vitamin":   ["Opti-Men", "Opti-Women", "Daily Multi", "Vitamin C 1000", "ZMA Recovery"],
    "fatburner": ["Hydroxycut", "Lipo-6 Black", "CLA 1000", "L-Carnitine 3000", "Thermo Cut"],
    "bar":       ["Protein Bar Coklat", "Crispy Wafer Bar", "Oat Energy Bar", "Peanut Protein Bar", "Brownie Bar"],
    "joint":     ["Glucosamine Plus", "Joint Support", "Collagen Peptides", "MSM Complex", "Flex Care"],
    "omega":     ["Fish Oil 1000mg", "Omega-3 Triple", "Krill Oil", "Cod Liver Oil", "Omega Complete"],
    "gear":      ["Shaker Bottle 600ml", "Lifting Straps", "Gym Gloves", "Wrist Wraps", "Lever Belt"],
    "isotonik":  ["Isotonic Drink", "Electrolyte Powder", "Hydro Boost", "Recovery Drink", "BCAA Hydrate"],
}

DEMO_FLAVOR = ["Cokelat", "Vanilla", "Strawberry", "Cookies & Cream", "Banana", "Mocha", "Unflavored", "Tropical"]
DEMO_SIZE = ["1 lb", "2 lb", "5 lb", "30 serv", "60 serv", "90 caps", "120 caps", "500 g"]


def make_demo(n=140):
    """Build a realistic demo catalogue. Some products get prices, some don't,
    so the 'Chat untuk harga' fallback is exercised alongside the price layer."""
    rng = random.Random(7)
    items = []
    for idx in range(1, n + 1):
        cat = DEMO_CATS[idx % len(DEMO_CATS)]
        brand = rng.choice(DEMO_BRANDS)
        typ = rng.choice(DEMO_TYPE[cat["k"]])
        flavor = rng.choice(DEMO_FLAVOR)
        size = rng.choice(DEMO_SIZE)
        title = f"{brand} {typ} {flavor} {size}".replace("  ", " ").strip()
        code = f"LMN{idx:04d}"
        p = {
            "c": code,
            "t": title,
            "k": cat["k"],
            "i": "",            # empty -> procedural SVG packshot (offline-safe demo)
            "q": round(rng.uniform(0.55, 0.99), 2),
        }
        # ~65% of demo products carry a price; the rest show "Chat untuk harga".
        if rng.random() < 0.65:
            base = rng.randint(12, 95) * 10000  # Rp120rb .. Rp950rb
            p["price"] = base
            if rng.random() < 0.45:
                p["compareAt"] = int(base * rng.choice([1.1, 1.15, 1.2, 1.25]) // 1000 * 1000)
        items.append(p)
    return items


def load_data():
    if os.path.exists(PRODUCTS_JSON):
        with open(PRODUCTS_JSON, "r", encoding="utf-8") as f:
            products = json.load(f)
    else:
        products = make_demo()
        with open(PRODUCTS_JSON, "w", encoding="utf-8") as f:
            json.dump(products, f, ensure_ascii=False, indent=0)
        print(f"  (seeded demo products.json with {len(products)} items)")

    if os.path.exists(CATS_JSON):
        with open(CATS_JSON, "r", encoding="utf-8") as f:
            cats = json.load(f)
    else:
        cats = DEMO_CATS
        with open(CATS_JSON, "w", encoding="utf-8") as f:
            json.dump(cats, f, ensure_ascii=False, indent=0)
        print(f"  (seeded demo cats.json with {len(cats)} categories)")

    return products, cats


def build_counts(products, cats):
    """Attach a live count to each category and drop empties to the end."""
    counts = {}
    for p in products:
        counts[p.get("k", "")] = counts.get(p.get("k", ""), 0) + 1
    out = []
    for c in cats:
        cc = dict(c)
        cc["count"] = counts.get(c["k"], 0)
        out.append(cc)
    return out


# --------------------------------------------------------------------------- #
#  HTML template  (single source -> two builds via CLEAN_BUILD flag)
# --------------------------------------------------------------------------- #

def render(products, cats, clean):
    data_json = json.dumps(products, ensure_ascii=False, separators=(",", ":"))
    cats_json = json.dumps(cats, ensure_ascii=False, separators=(",", ":"))
    tmpl = TEMPLATE
    tmpl = tmpl.replace("/*__PRODUCTS__*/[]", data_json)
    tmpl = tmpl.replace("/*__CATS__*/[]", cats_json)
    tmpl = tmpl.replace("/*__CLEAN__*/false", "true" if clean else "false")
    return tmpl


def main():
    products, cats = load_data()
    cats = build_counts(products, cats)
    print(f"LIMITLESS build: {len(products)} products, {len(cats)} categories")

    with open(OUT_PROXY, "w", encoding="utf-8") as f:
        f.write(render(products, cats, clean=False))
    print(f"  -> {os.path.relpath(OUT_PROXY, ROOT)}  (weserv proxy images)")

    with open(OUT_CLEAN, "w", encoding="utf-8") as f:
        f.write(render(products, cats, clean=True))
    print(f"  -> {os.path.relpath(OUT_CLEAN, ROOT)}  (local images_clean/)")

    print("Done.")


# The template is defined at module bottom to keep main() readable.
TEMPLATE = r"""<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0A0A0A">
<title>LIMITLESS — Suplemen Nutrisi & Fitness Original | Bali</title>
<meta name="description" content="LIMITLESS — reseller suplemen nutrisi & fitness original di Bali. Whey, mass gainer, pre-workout, vitamin. Original, BPOM, Halal MUI, COD se-Indonesia, garansi 30 hari.">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230A0A0A'/%3E%3Ctext x='50%25' y='54%25' font-family='Arial Black,Arial' font-weight='900' font-size='30' fill='%23FF6A00' text-anchor='middle' dominant-baseline='middle'%3ELG%3C/text%3E%3C/svg%3E">
<meta property="og:type" content="website">
<meta property="og:site_name" content="LIMITLESS">
<meta property="og:title" content="LIMITLESS — Suplemen Nutrisi & Fitness Original | Bali">
<meta property="og:description" content="Reseller suplemen original di Bali. Original, BPOM, Halal MUI, COD se-Indonesia, garansi 30 hari.">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800;900&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<style>
:root{
  --page:#FFFFFF; --text:#111111; --muted:#5A5A57; --bone:#F4F2ED; --deep-bone:#ECE9E2;
  --cta:#0A0A0A; --hair:#E4E1DA; --wa:#1EBE5D; --check:#2FA968; --accent:#FF6A00;
  --nav-h:64px; --r:14px; --maxw:1280px;
  --shadow:0 1px 2px rgba(17,17,17,.04),0 8px 24px rgba(17,17,17,.06);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--page); color:var(--text);
  font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  font-size:15px; line-height:1.5; overflow-x:hidden;
}
img{max-width:100%; display:block}
button{font-family:inherit; cursor:pointer; border:0; background:none; color:inherit}
a{color:inherit; text-decoration:none}
h1,h2,h3,h4{font-family:Archivo,sans-serif; margin:0; letter-spacing:-.01em; font-weight:800}
.wrap{max-width:var(--maxw); margin:0 auto; padding:0 20px}
.label{font-family:Archivo,sans-serif; font-weight:800; text-transform:uppercase; letter-spacing:.14em; font-size:11px}
.muted{color:var(--muted)}
.btn{font-family:Archivo,sans-serif; font-weight:800; text-transform:uppercase; letter-spacing:.1em; font-size:12px;
  background:var(--cta); color:#fff; padding:14px 22px; border-radius:999px; display:inline-flex; align-items:center;
  justify-content:center; gap:8px; min-height:48px; transition:transform .15s ease,opacity .15s ease}
.btn:hover{transform:translateY(-1px)}
.btn:active{transform:translateY(0)}
.btn.ghost{background:transparent; color:var(--text); border:1.5px solid var(--text)}
.btn.bone{background:var(--bone); color:var(--text)}
.btn.wa{background:var(--wa); color:#fff}
.btn.block{width:100%}
.pill{display:inline-flex; align-items:center; gap:6px; background:var(--bone); border:1px solid var(--hair);
  padding:6px 12px; border-radius:999px; font-size:12px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}

/* ---------- NAV ---------- */
.nav{position:sticky; top:0; z-index:60; background:rgba(255,255,255,.82); backdrop-filter:saturate(180%) blur(14px);
  border-bottom:1px solid var(--hair)}
.nav-in{display:flex; align-items:center; gap:18px; height:var(--nav-h)}
.brand{display:flex; align-items:center; gap:10px; font-family:Archivo; font-weight:900; font-size:20px; letter-spacing:.04em}
.brand img{height:30px; width:auto}
.brand .lg{width:34px;height:34px;border-radius:9px;background:var(--cta);display:flex;align-items:center;justify-content:center;
  color:var(--accent);font-weight:900;font-size:15px}
.nav-links{display:flex; gap:4px; margin-left:6px}
.nav-links>button{padding:10px 14px; border-radius:10px; font-family:Archivo; font-weight:800; text-transform:uppercase;
  letter-spacing:.08em; font-size:12px; color:var(--text)}
.nav-links>button:hover{background:var(--bone)}
.nav-spacer{flex:1}
.nav-search{position:relative; width:min(360px,34vw)}
.nav-search input{width:100%; height:44px; border:1px solid var(--hair); border-radius:999px; padding:0 42px 0 16px;
  background:var(--bone); font-size:14px; outline:none}
.nav-search input:focus{border-color:var(--text); background:#fff}
.nav-search .ic{position:absolute; right:14px; top:50%; transform:translateY(-50%); opacity:.5}
.nav-ico{display:flex; gap:6px}
.iconbtn{position:relative; width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center}
.iconbtn:hover{background:var(--bone)}
.badge{position:absolute; top:4px; right:4px; min-width:18px; height:18px; padding:0 4px; border-radius:999px;
  background:var(--cta); color:#fff; font-size:11px; font-weight:700; display:flex; align-items:center; justify-content:center;
  font-family:Inter}
.hamb{display:none}

/* search suggestions */
.suggest{position:absolute; top:50px; left:0; right:0; background:#fff; border:1px solid var(--hair); border-radius:14px;
  box-shadow:var(--shadow); overflow:hidden; z-index:80; display:none}
.suggest.open{display:block}
.suggest a{display:flex; gap:10px; align-items:center; padding:10px 12px; border-bottom:1px solid var(--hair)}
.suggest a:last-child{border-bottom:0}
.suggest a:hover{background:var(--bone)}
.suggest img,.suggest .ph{width:40px; height:40px; border-radius:8px; object-fit:cover; background:var(--bone); flex:0 0 40px}
.suggest .st{font-size:13px; line-height:1.3}
.suggest .sc{font-size:11px; color:var(--muted)}

/* mega menu */
.mega{position:absolute; top:var(--nav-h); left:0; right:0; background:#fff; border-bottom:1px solid var(--hair);
  box-shadow:var(--shadow); z-index:55; display:none}
.mega.open{display:block}
.mega-in{display:grid; grid-template-columns:1.6fr 1fr; gap:30px; padding:26px 0}
.mega-cols{display:grid; grid-template-columns:repeat(3,1fr); gap:8px 22px}
.mega-cols button{display:flex; justify-content:space-between; align-items:center; padding:9px 10px; border-radius:9px; text-align:left}
.mega-cols button:hover{background:var(--bone)}
.mega-cols .cn{font-size:13px}
.mega-cols .cc{font-size:11px; color:var(--muted)}
.mega-feature{background:var(--bone); border-radius:var(--r); padding:20px; display:flex; flex-direction:column; justify-content:space-between}
.mega-quick{display:flex; flex-wrap:wrap; gap:8px; margin-top:10px}

/* ---------- HERO ---------- */
.hero{background:var(--bone); border-bottom:1px solid var(--hair); overflow:hidden}
.hero-in{display:grid; grid-template-columns:1.1fr .9fr; gap:30px; align-items:center; padding:54px 0}
.hero h1{font-size:clamp(34px,5.2vw,62px); font-weight:900; line-height:.98; letter-spacing:-.02em}
.hero h1 em{font-style:normal; color:var(--accent)}
.hero p{color:var(--muted); font-size:16px; max-width:46ch; margin:18px 0 24px}
.hero-cta{display:flex; gap:12px; flex-wrap:wrap}
.hero-trust{display:flex; flex-wrap:wrap; gap:8px; margin-top:22px}
.hero-canvas{aspect-ratio:1/1; width:100%; max-width:460px; margin:0 auto; touch-action:none}

/* trust strip */
.trust-strip{border-bottom:1px solid var(--hair)}
.trust-strip .wrap{display:flex; flex-wrap:wrap; gap:8px 26px; padding:14px 20px; justify-content:center}
.trust-strip span{display:flex; align-items:center; gap:7px; font-size:12px; color:var(--muted)}

/* ---------- SECTIONS ---------- */
section{padding:46px 0}
.sec-head{display:flex; align-items:flex-end; justify-content:space-between; gap:16px; margin-bottom:22px}
.sec-head h2{font-size:clamp(22px,3vw,32px); font-weight:900}
.sec-head .label{color:var(--accent); display:block; margin-bottom:8px}

/* chips */
.chips{display:flex; gap:8px; overflow-x:auto; padding-bottom:6px; -webkit-overflow-scrolling:touch}
.chips::-webkit-scrollbar{height:0}
.chip{flex:0 0 auto; padding:9px 16px; border-radius:999px; border:1px solid var(--hair); background:#fff;
  font-family:Archivo; font-weight:800; text-transform:uppercase; letter-spacing:.06em; font-size:11px; white-space:nowrap}
.chip.on{background:var(--cta); color:#fff; border-color:var(--cta)}

.toolbar{display:flex; gap:12px; align-items:center; justify-content:space-between; margin-bottom:18px; flex-wrap:wrap}
.toolbar .left{display:flex; gap:10px; align-items:center; flex:1; min-width:0}
.toolbar select{height:44px; border:1px solid var(--hair); border-radius:10px; padding:0 12px; background:#fff; font-size:13px}
.count-note{font-size:13px; color:var(--muted)}

/* grid + cards */
.grid{display:grid; grid-template-columns:repeat(4,1fr); gap:18px}
.card{border:1px solid var(--hair); border-radius:var(--r); background:#fff; overflow:hidden; display:flex; flex-direction:column;
  transition:transform .18s ease, box-shadow .18s ease}
.card:hover{transform:translateY(-3px); box-shadow:var(--shadow)}
.card .media{position:relative; aspect-ratio:1/1; background:var(--bone); cursor:pointer}
.card .media img{width:100%; height:100%; object-fit:contain; padding:10%}
.card .media.skel{background:linear-gradient(100deg,var(--bone) 30%,var(--deep-bone) 50%,var(--bone) 70%);
  background-size:200% 100%; animation:shimmer 1.3s infinite}
@keyframes shimmer{to{background-position:-200% 0}}
.heart{position:absolute; top:10px; right:10px; width:38px; height:38px; border-radius:999px; background:rgba(255,255,255,.9);
  display:flex; align-items:center; justify-content:center; box-shadow:var(--shadow)}
.heart svg{width:18px;height:18px}
.heart.on svg{fill:#E23744; stroke:#E23744}
.tag-disc{position:absolute; top:10px; left:10px; background:var(--accent); color:#fff; font-family:Archivo; font-weight:800;
  font-size:11px; padding:5px 9px; border-radius:8px; letter-spacing:.04em}
.card .body{padding:13px 14px 15px; display:flex; flex-direction:column; gap:9px; flex:1}
.card .cat{font-size:10.5px; color:var(--muted); text-transform:uppercase; letter-spacing:.1em; font-family:Archivo; font-weight:800}
.card .title{font-size:13.5px; line-height:1.35; font-weight:600; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;
  overflow:hidden; min-height:2.7em; cursor:pointer}
.benefits{display:flex; flex-direction:column; gap:5px; margin:2px 0}
.benefits li{display:flex; gap:7px; align-items:flex-start; font-size:11.5px; color:var(--muted); list-style:none}
.benefits svg{flex:0 0 14px; width:14px; height:14px; margin-top:1px}
.benefits{padding:0;margin:2px 0}
.price-row{display:flex; align-items:baseline; gap:8px; margin-top:auto}
.price{font-family:Archivo; font-weight:900; font-size:16px}
.compare{font-size:12px; color:var(--muted); text-decoration:line-through}
.price.ask{font-size:13px; font-weight:800; color:var(--muted)}
.card .add{margin-top:4px}
.load-more{display:flex; justify-content:center; margin-top:30px}

/* rails */
.rail{display:grid; grid-auto-flow:column; grid-auto-columns:minmax(220px,1fr); gap:16px; overflow-x:auto; padding-bottom:8px;
  scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch}
.rail::-webkit-scrollbar{height:0}
.rail>*{scroll-snap-align:start}

/* category showcase */
.cat-show{display:grid; grid-template-columns:repeat(4,1fr); gap:14px}
.cat-tile{position:relative; border-radius:var(--r); background:var(--deep-bone); padding:22px 18px; min-height:130px;
  display:flex; flex-direction:column; justify-content:space-between; border:1px solid var(--hair); overflow:hidden}
.cat-tile:hover{background:var(--bone)}
.cat-tile h3{font-size:16px; font-weight:900}
.cat-tile .cc{font-size:12px; color:var(--muted)}
.cat-tile .arrow{align-self:flex-end; font-size:20px}

/* editorial bands */
.band-black{background:var(--cta); color:#fff}
.band-black .wrap{padding:64px 20px; text-align:center}
.band-black h2{font-size:clamp(26px,4.5vw,52px); font-weight:900; line-height:1.02; max-width:18ch; margin:0 auto}
.band-black p{color:#cfcfca; max-width:52ch; margin:18px auto 0}
.split{display:grid; grid-template-columns:1fr 1fr; gap:0; align-items:stretch; border-top:1px solid var(--hair); border-bottom:1px solid var(--hair)}
.split .pane{padding:54px 40px; display:flex; flex-direction:column; justify-content:center}
.split .pane.bone{background:var(--bone)}
.stats{display:grid; grid-template-columns:repeat(3,1fr); gap:18px; margin-top:24px}
.stats .n{font-family:Archivo; font-weight:900; font-size:30px; color:var(--accent)}
.stats .l{font-size:12px; color:var(--muted)}
.community{background:var(--bone); border-top:1px solid var(--hair)}

/* footer */
footer{background:var(--cta); color:#cfcfca; padding:50px 0 120px}
footer .cols{display:grid; grid-template-columns:1.5fr 1fr 1fr 1fr; gap:30px}
footer h4{color:#fff; font-size:13px; text-transform:uppercase; letter-spacing:.12em; margin-bottom:14px}
footer a{display:block; padding:5px 0; font-size:13px}
footer a:hover{color:#fff}
footer .pay{display:flex; flex-wrap:wrap; gap:6px; margin-top:10px}
footer .pay span{border:1px solid #2a2a2a; border-radius:7px; padding:5px 9px; font-size:11px; color:#bdbdb8}
.copy{border-top:1px solid #222; margin-top:34px; padding-top:18px; font-size:12px; display:flex; justify-content:space-between; gap:14px; flex-wrap:wrap}

/* ---------- DRAWERS / MODALS ---------- */
.scrim{position:fixed; inset:0; background:rgba(10,10,10,.45); z-index:90; opacity:0; pointer-events:none; transition:opacity .25s}
.scrim.open{opacity:1; pointer-events:auto}
.drawer{position:fixed; top:0; right:0; height:100%; width:min(420px,92vw); background:#fff; z-index:95; transform:translateX(100%);
  transition:transform .3s cubic-bezier(.4,0,.2,1); display:flex; flex-direction:column}
.drawer.open{transform:translateX(0)}
.drawer.left{left:0; right:auto; transform:translateX(-100%); width:min(360px,88vw)}
.drawer.left.open{transform:translateX(0)}
.drawer-head{display:flex; align-items:center; justify-content:space-between; padding:18px 20px; border-bottom:1px solid var(--hair)}
.drawer-head h3{font-size:16px; text-transform:uppercase; letter-spacing:.08em}
.drawer-body{flex:1; overflow-y:auto; padding:16px 20px}
.drawer-foot{border-top:1px solid var(--hair); padding:16px 20px; display:flex; flex-direction:column; gap:10px}
.close-x{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:20px}
.close-x:hover{background:var(--bone)}

/* cart line */
.cart-line{display:grid; grid-template-columns:64px 1fr auto; gap:12px; padding:14px 0; border-bottom:1px solid var(--hair)}
.cart-line .thumb{width:64px;height:64px;border-radius:10px;background:var(--bone);object-fit:contain;padding:6px}
.cart-line .ct{font-size:13px; font-weight:600; line-height:1.3}
.cart-line .cc{font-size:11px; color:var(--muted)}
.qty{display:inline-flex; align-items:center; border:1px solid var(--hair); border-radius:999px; overflow:hidden}
.qty button{width:32px;height:32px; font-size:16px; display:flex;align-items:center;justify-content:center}
.qty button:hover{background:var(--bone)}
.qty span{min-width:30px; text-align:center; font-size:13px; font-weight:600}
.cart-line .rm{font-size:11px; color:var(--muted); text-decoration:underline; margin-top:6px}
.subtotal{display:flex; justify-content:space-between; align-items:baseline; font-family:Archivo; font-weight:900; font-size:18px}
.empty-state{text-align:center; padding:50px 10px; color:var(--muted)}

/* fulfillment */
.fulfill{display:flex; flex-direction:column; gap:10px; margin-bottom:6px}
.seg{display:flex; gap:6px; background:var(--bone); border-radius:999px; padding:4px}
.seg button{flex:1; padding:10px; border-radius:999px; font-family:Archivo; font-weight:800; font-size:11.5px;
  text-transform:uppercase; letter-spacing:.06em}
.seg button.on{background:#fff; box-shadow:var(--shadow)}
.fulfill select{width:100%; height:44px; border:1px solid var(--hair); border-radius:10px; padding:0 12px; background:#fff; font-size:13px}

/* quick view */
.qv{position:fixed; inset:0; z-index:96; display:none; align-items:center; justify-content:center; padding:18px}
.qv.open{display:flex}
.qv-card{background:#fff; border-radius:18px; width:min(900px,96vw); max-height:92vh; overflow-y:auto; position:relative;
  display:grid; grid-template-columns:1fr 1fr}
.qv-media{background:var(--bone); aspect-ratio:1/1; display:flex; align-items:center; justify-content:center; padding:8%}
.qv-media img{width:100%;height:100%;object-fit:contain}
.qv-info{padding:30px 28px}
.qv-info .cat{font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.1em; font-family:Archivo; font-weight:800}
.qv-info h2{font-size:24px; font-weight:900; margin:8px 0 12px; line-height:1.1}
.qv-price{display:flex; align-items:baseline; gap:10px; margin:10px 0 16px}
.qv-price .price{font-size:24px}
.qv-close{position:absolute; top:12px; right:12px; background:#fff; z-index:2}
.qv-actions{display:flex; gap:10px; margin:18px 0; flex-wrap:wrap}
.qv-related{padding:0 28px 28px; grid-column:1/-1}
.qv-related h4{font-size:12px; text-transform:uppercase; letter-spacing:.1em; margin-bottom:12px; color:var(--muted)}

/* buy bar (desktop) */
.buybar{position:fixed; bottom:0; left:0; right:0; z-index:50; background:rgba(255,255,255,.95); backdrop-filter:blur(10px);
  border-top:1px solid var(--hair); transform:translateY(110%); transition:transform .3s}
.buybar.show{transform:translateY(0)}
.buybar .wrap{display:flex; align-items:center; gap:16px; padding:12px 20px}
.buybar .bt{flex:1; font-weight:600}
.buybar .bp{font-family:Archivo; font-weight:900; font-size:18px}

/* FAB + back to top */
.fab{position:fixed; right:18px; bottom:84px; z-index:55; width:56px; height:56px; border-radius:999px; background:var(--wa);
  color:#fff; display:flex; align-items:center; justify-content:center; box-shadow:0 8px 24px rgba(30,190,93,.4)}
.fab svg{width:28px;height:28px}
.totop{position:fixed; left:18px; bottom:84px; z-index:55; width:46px; height:46px; border-radius:999px; background:var(--cta);
  color:#fff; display:none; align-items:center; justify-content:center}
.totop.show{display:flex}

/* mobile tab bar */
.tabbar{display:none; position:fixed; bottom:0; left:0; right:0; z-index:58; background:rgba(255,255,255,.96);
  backdrop-filter:blur(12px); border-top:1px solid var(--hair); padding-bottom:env(safe-area-inset-bottom)}
.tabbar .tabs{display:grid; grid-template-columns:repeat(5,1fr)}
.tabbar button{position:relative; padding:9px 0 8px; display:flex; flex-direction:column; align-items:center; gap:3px;
  font-size:10px; font-family:Archivo; font-weight:800; text-transform:uppercase; letter-spacing:.04em; color:var(--muted)}
.tabbar button.on{color:var(--text)}
.tabbar svg{width:22px; height:22px}
.tabbar .badge{top:2px; right:calc(50% - 22px)}

/* mobile drawer nav list */
.mnav a,.mnav button{display:flex; justify-content:space-between; align-items:center; width:100%; padding:14px 4px;
  border-bottom:1px solid var(--hair); font-family:Archivo; font-weight:800; text-transform:uppercase; letter-spacing:.06em;
  font-size:13px; text-align:left}

/* toast */
.toast{position:fixed; left:50%; bottom:100px; transform:translateX(-50%) translateY(20px); background:var(--cta); color:#fff;
  padding:12px 20px; border-radius:999px; font-size:13px; z-index:120; opacity:0; pointer-events:none; transition:all .25s;
  display:flex; gap:10px; align-items:center}
.toast.show{opacity:1; transform:translateX(-50%) translateY(0)}

/* ---------- RESPONSIVE ---------- */
@media(max-width:1024px){
  .grid{grid-template-columns:repeat(3,1fr)}
  .cat-show{grid-template-columns:repeat(2,1fr)}
  .mega-in{grid-template-columns:1fr}
}
@media(max-width:768px){
  .nav-links,.nav-search,.buybar{display:none}
  .hamb{display:flex}
  .hero-in{grid-template-columns:1fr; padding:34px 0; text-align:center}
  .hero p{margin-left:auto;margin-right:auto}
  .hero-cta,.hero-trust{justify-content:center}
  .hero-canvas{max-width:300px; order:-1}
  .grid{grid-template-columns:repeat(2,1fr); gap:12px}
  .split{grid-template-columns:1fr}
  footer .cols{grid-template-columns:1fr 1fr}
  footer{padding-bottom:130px}
  .qv-card{grid-template-columns:1fr}
  .qv-media{aspect-ratio:16/11}
  .tabbar{display:block}
  .fab{bottom:78px}
  .totop{bottom:78px}
  .card .benefits{display:none}
}
@media(max-width:430px){
  .grid{gap:10px}
  .cat-show{grid-template-columns:1fr 1fr}
  .stats{grid-template-columns:1fr 1fr}
}
@media (prefers-reduced-motion: reduce){
  *{animation-duration:.001ms !important; transition-duration:.001ms !important}
}
</style>
</head>
<body>

<!-- ===================== NAV ===================== -->
<header class="nav">
  <div class="wrap nav-in">
    <button class="iconbtn hamb" onclick="openDrawer('mdrawer')" aria-label="Menu">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    </button>
    <a class="brand" href="#" onclick="goHome();return false" aria-label="LIMITLESS beranda">
      <img src="logo.png" alt="LIMITLESS" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
      <span class="lg" style="display:none">LG</span>
      <span>LIMITLESS</span>
    </a>
    <nav class="nav-links">
      <button onclick="toggleMega('belanja')" id="mb-belanja">Belanja</button>
      <button onclick="toggleMega('tujuan')" id="mb-tujuan">Tujuan</button>
      <button onclick="scrollToGrid()">Terlaris</button>
      <button onclick="filterByCat('');scrollToGrid()">Semua Produk</button>
    </nav>
    <div class="nav-spacer"></div>
    <div class="nav-search">
      <input id="searchInput" type="search" placeholder="Cari whey, creatine, vitamin…" autocomplete="off"
        oninput="onSearch(this.value)" onfocus="onSearch(this.value)" aria-label="Cari produk">
      <span class="ic"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg></span>
      <div class="suggest" id="suggest"></div>
    </div>
    <div class="nav-ico">
      <button class="iconbtn" onclick="toggleWishlistFilter()" id="wishBtn" aria-label="Favorit">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 1 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>
        <span class="badge" id="wishBadge" style="display:none">0</span>
      </button>
      <button class="iconbtn" onclick="openDrawer('cart')" aria-label="Keranjang">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></svg>
        <span class="badge" id="cartBadge" style="display:none">0</span>
      </button>
    </div>
  </div>
  <!-- mega menus -->
  <div class="mega" id="mega-belanja">
    <div class="wrap mega-in">
      <div>
        <span class="label" style="color:var(--accent)">Belanja per Kategori</span>
        <div class="mega-cols" id="megaCats" style="margin-top:14px"></div>
        <div style="margin-top:18px">
          <span class="label muted">Cari Cepat</span>
          <div class="mega-quick" id="megaQuick"></div>
        </div>
      </div>
      <div class="mega-feature">
        <div>
          <span class="label" style="color:var(--accent)">Pilihan Editor</span>
          <h3 style="font-size:22px;margin:10px 0 6px">Paket Bulking Hemat</h3>
          <p class="muted" style="font-size:13px">Whey + Mass Gainer + Creatine. Stok original, COD se-Indonesia.</p>
        </div>
        <button class="btn" style="margin-top:16px" onclick="filterByCat('gainer');closeMega();scrollToGrid()">Lihat Mass Gainer</button>
      </div>
    </div>
  </div>
  <div class="mega" id="mega-tujuan">
    <div class="wrap mega-in">
      <div>
        <span class="label" style="color:var(--accent)">Belanja per Tujuan</span>
        <div class="mega-cols" id="megaGoals" style="margin-top:14px"></div>
      </div>
      <div class="mega-feature">
        <div>
          <span class="label" style="color:var(--accent)">Konsultasi Gratis</span>
          <h3 style="font-size:22px;margin:10px 0 6px">Bingung pilih?</h3>
          <p class="muted" style="font-size:13px">Chat admin LIMITLESS, kami bantu susun program sesuai tujuanmu.</p>
        </div>
        <button class="btn wa" style="margin-top:16px" onclick="waConsult()">Chat Admin</button>
      </div>
    </div>
  </div>
</header>

<!-- ===================== HERO ===================== -->
<section class="hero" style="padding:0">
  <div class="wrap hero-in">
    <div>
      <span class="label" style="color:var(--accent)">Nutrition & Fitness · Bali</span>
      <h1 style="margin-top:14px">JADI VERSI<br><em>TANPA BATAS</em><br>DIRIMU.</h1>
      <p>Suplemen original, BPOM &amp; Halal MUI. Whey, mass gainer, pre-workout, vitamin — dikirim cepat ke seluruh Indonesia.</p>
      <div class="hero-cta">
        <button class="btn" onclick="scrollToGrid()">Belanja Sekarang</button>
        <button class="btn ghost" onclick="waConsult()">Konsultasi Gratis</button>
      </div>
      <div class="hero-trust" id="heroTrust"></div>
    </div>
    <canvas class="hero-canvas" id="tub" aria-label="Produk LIMITLESS 3D"></canvas>
  </div>
</section>

<!-- trust strip -->
<div class="trust-strip"><div class="wrap" id="trustStrip"></div></div>

<!-- ===================== CATEGORY SHOWCASE ===================== -->
<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="label">Telusuri</span><h2>Belanja per Kategori</h2></div></div>
    <div class="cat-show" id="catShow"></div>
  </div>
</section>

<!-- ===================== BEST SELLERS RAIL ===================== -->
<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><span class="label">Paling Dicari</span><h2>Best Seller</h2></div>
      <button class="btn bone" onclick="setSort('terlaris');scrollToGrid()">Lihat Semua</button></div>
    <div class="rail" id="bestRail"></div>
  </div>
</section>

<!-- ===================== MANIFESTO BAND ===================== -->
<div class="band-black">
  <div class="wrap">
    <span class="label" style="color:var(--accent)">Manifesto</span>
    <h2 style="margin-top:14px">PROGRES BUKAN SOAL KEBERUNTUNGAN. ITU SOAL BAHAN BAKAR.</h2>
    <p>Kami kurasi hanya suplemen original bersertifikat untuk mendukung setiap repetisi, setiap langkah, setiap target. Tanpa kompromi.</p>
  </div>
</div>

<!-- ===================== MAIN GRID ===================== -->
<section id="shop">
  <div class="wrap">
    <div class="sec-head"><div><span class="label">Katalog</span><h2 id="gridTitle">Semua Produk</h2></div></div>
    <div class="chips" id="chips" style="margin-bottom:16px"></div>
    <div class="toolbar">
      <div class="left"><span class="count-note" id="countNote"></span></div>
      <select id="sortSel" onchange="setSort(this.value)" aria-label="Urutkan">
        <option value="relevan">Urutkan: Relevan</option>
        <option value="terlaris">Terlaris</option>
        <option value="harga-asc">Harga: Terendah</option>
        <option value="harga-desc">Harga: Tertinggi</option>
        <option value="az">Nama: A–Z</option>
      </select>
    </div>
    <div class="grid" id="grid"></div>
    <div class="load-more" id="loadMoreWrap"><button class="btn bone" id="loadMore" onclick="loadMore()">Muat Lebih Banyak</button></div>
  </div>
</section>

<!-- ===================== SPLIT (image/stats) ===================== -->
<div class="split">
  <div class="pane bone">
    <span class="label" style="color:var(--accent)">Kenapa LIMITLESS</span>
    <h2 style="font-size:clamp(24px,3.4vw,36px);margin:12px 0 10px">Original. Bergaransi. Dekat.</h2>
    <p class="muted">Setiap produk dijamin keasliannya. Salah barang atau rusak? Garansi 30 hari. Ambil langsung di cabang atau kirim hari ini juga.</p>
    <div class="stats">
      <div><div class="n">2.500+</div><div class="l">Produk Original</div></div>
      <div><div class="n">30 Hari</div><div class="l">Garansi Tukar</div></div>
      <div><div class="n">100%</div><div class="l">BPOM & Halal</div></div>
    </div>
  </div>
  <div class="pane" style="background:var(--cta);color:#fff">
    <span class="label" style="color:var(--accent)">Fulfillment</span>
    <h2 style="font-size:clamp(24px,3.4vw,36px);margin:12px 0 10px;color:#fff">Dikirim atau Ambil di Cabang.</h2>
    <p style="color:#cfcfca">Pilih kurir Gojek / Grab / Maxim / reguler, atau ambil sendiri di cabang terdekat. Bayar QRIS, e-wallet, VA, atau COD.</p>
    <div class="hero-cta" style="margin-top:20px">
      <button class="btn" style="background:#fff;color:#0A0A0A" onclick="scrollToGrid()">Mulai Belanja</button>
      <button class="btn wa" onclick="waConsult()">Chat Admin</button>
    </div>
  </div>
</div>

<!-- ===================== RECENTLY VIEWED ===================== -->
<section id="recentSec" style="display:none">
  <div class="wrap">
    <div class="sec-head"><div><span class="label">Riwayat</span><h2>Baru Dilihat</h2></div></div>
    <div class="rail" id="recentRail"></div>
  </div>
</section>

<!-- ===================== COMMUNITY ===================== -->
<div class="community"><div class="wrap" style="padding:54px 20px;text-align:center">
  <span class="label" style="color:var(--accent)">#TeamLimitless</span>
  <h2 style="font-size:clamp(24px,3.6vw,40px);margin:12px auto;max-width:20ch">Bergabung dengan ribuan member di seluruh Indonesia.</h2>
  <p class="muted" style="max-width:50ch;margin:0 auto 20px">Tips latihan, promo eksklusif, dan rilis produk baru langsung di WhatsApp.</p>
  <button class="btn wa" onclick="waConsult()">Gabung via WhatsApp</button>
</div></div>

<!-- ===================== FOOTER ===================== -->
<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <div class="brand" style="color:#fff;font-size:22px"><span class="lg">LG</span><span>LIMITLESS</span></div>
        <p style="margin:14px 0 0;max-width:34ch">Reseller suplemen nutrisi &amp; fitness original. Bali, melayani seluruh Indonesia.</p>
        <div class="pay" id="footPay"></div>
      </div>
      <div><h4>Belanja</h4><div id="footCats"></div></div>
      <div><h4>Bantuan</h4>
        <a href="#" onclick="waConsult();return false">Chat Admin</a>
        <a href="#" onclick="waConsult();return false">Cek Ongkir</a>
        <a href="#" onclick="waConsult();return false">Status Pesanan</a>
        <a href="#" onclick="waConsult();return false">Garansi 30 Hari</a>
      </div>
      <div><h4>Cabang</h4><div id="footBranches"></div></div>
    </div>
    <div class="copy"><span>© 2026 LIMITLESS. Semua hak dilindungi.</span><span>Original · BPOM · Halal MUI</span></div>
  </div>
</footer>

<!-- ===================== OVERLAYS ===================== -->
<div class="scrim" id="scrim" onclick="closeAll()"></div>

<!-- mobile drawer -->
<aside class="drawer left" id="mdrawer">
  <div class="drawer-head"><h3>Menu</h3><button class="close-x" onclick="closeAll()">✕</button></div>
  <div class="drawer-body mnav" id="mnav"></div>
</aside>

<!-- cart drawer -->
<aside class="drawer" id="cart">
  <div class="drawer-head"><h3>Keranjang</h3><button class="close-x" onclick="closeAll()">✕</button></div>
  <div class="drawer-body" id="cartBody"></div>
  <div class="drawer-foot" id="cartFoot"></div>
</aside>

<!-- quick view -->
<div class="qv" id="qv"><div class="qv-card" id="qvCard"></div></div>

<!-- buy bar -->
<div class="buybar" id="buybar"><div class="wrap">
  <span class="bt" id="bbTitle"></span><span class="bp" id="bbPrice"></span>
  <button class="btn" onclick="addToCart(BB_CODE,1)">Tambah ke Keranjang</button>
</div></div>

<!-- mobile tab bar -->
<nav class="tabbar"><div class="tabs">
  <button onclick="goHome()" class="on" id="tab-home"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/></svg>Beranda</button>
  <button onclick="toggleMega('belanja');closeAll()" id="tab-cat"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>Kategori</button>
  <button onclick="focusSearch()" id="tab-search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.5" y2="16.5"/></svg>Cari</button>
  <button onclick="toggleWishlistFilter()" id="tab-fav"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 1 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>Favorit<span class="badge" id="favTabBadge" style="display:none">0</span></button>
  <button onclick="openDrawer('cart')" id="tab-cart"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></svg>Keranjang<span class="badge" id="cartTabBadge" style="display:none">0</span></button>
</div></nav>

<!-- FAB + back to top + toast -->
<button class="fab" onclick="waConsult()" aria-label="Chat WhatsApp"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.82 11.82 0 0 1 8.413 3.488 11.82 11.82 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 0 0 1.51 5.26l-.999 3.648 3.978-1.607zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.096 3.2 5.077 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413z"/></svg></button>
<button class="totop" id="totop" onclick="window.scrollTo({top:0,behavior:'smooth'})" aria-label="Ke atas">↑</button>
<div class="toast" id="toast"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
/* ===================== CONFIG — single source of truth ===================== */
const CONFIG = {
  brand:"LIMITLESS",
  waAdmins:["628989755534","6289518200002","6281339229918"],
  couriers:["Gojek","Grab","Maxim","Kurir Reguler (JNE/J&T/SiCepat)"],
  branches:[
    {n:"Cabang Sanur (Pusat)", a:"", wa:""}
    // Tambah cabang lain: {n:"Cabang Denpasar", a:"Jl. ...", wa:"628xxxxxxxxxx"}
  ],
  payEndpoint:"",      // isi URL gateway (Xendit/Midtrans/n8n) -> payOnline() aktif
  analyticsId:"",      // isi GA4 ID "G-XXXX" atau Meta Pixel ID -> snippet di-inject; kosong = tidak ada
  trust:["Original","BPOM","Halal MUI","COD","Gratis Ongkir","Garansi 30 Hari"]
};

/* ===================== DATA (injected by build_store2.py) ===================== */
const PRODUCTS = /*__PRODUCTS__*/[];
const CATS = /*__CATS__*/[];
const CLEAN_BUILD = /*__CLEAN__*/false;

const GOALS = [
  {g:"massa",     n:"Naik Massa / Bulking"},
  {g:"diet",      n:"Diet / Cutting"},
  {g:"performa",  n:"Energi & Performa"},
  {g:"pemulihan", n:"Pemulihan / Recovery"},
  {g:"kesehatan", n:"Kesehatan Umum"}
];
const PAY_BADGES = ["QRIS","GoPay","OVO","DANA","ShopeePay","BCA VA","COD"];
const BENEFITS = ["100% Original bersegel","BPOM & Halal MUI","Garansi 30 hari"];
const PAGE = 20;

/* ===================== STATE ===================== */
let state = { cat:"", q:"", sort:"relevan", wishOnly:false, goal:"", page:1 };
let cart = {};                 // {code: qty}
let wishlist = new Set();
let recent = [];               // codes, most-recent first
let fulfillMode = "kirim";     // "kirim" | "ambil"
let BB_CODE = "";
const byCode = {};
PRODUCTS.forEach(p => byCode[p.c] = p);
const catName = {}; CATS.forEach(c => catName[c.k] = c.n);

/* ===================== HELPERS ===================== */
const money = n => "Rp " + Number(n).toLocaleString("id-ID");
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const enc = encodeURIComponent;
function priceHtml(p, big){
  if(p.price==null) return '<span class="price ask">Chat untuk harga</span>';
  let h = '<span class="price">'+money(p.price)+'</span>';
  if(p.compareAt && p.compareAt>p.price) h += '<span class="compare">'+money(p.compareAt)+'</span>';
  return h;
}
function discPct(p){ return (p.compareAt && p.price && p.compareAt>p.price) ? Math.round((1-p.price/p.compareAt)*100) : 0; }

/* image source resolution — keeps the local->proxy->SVG fallback chain intact */
function img(p){
  if(CLEAN_BUILD) return "images_clean/" + p.c + ".webp";
  const u = p.i || "";
  if(u.indexOf("http") === 0) return "https://images.weserv.nl/?url=" + enc(u.replace(/^https?:\/\//,'')) + "&w=600&output=webp&q=82";
  return u;
}
function imgFallback(p){
  // clean build: webp missing -> try proxied remote; remote build/no url -> SVG packshot
  if(CLEAN_BUILD && p.i){
    return "this.onerror=function(){this.src='"+svgPack(p)+"'};this.src='https://images.weserv.nl/?url="+enc(p.i.replace(/^https?:\/\//,''))+"&w=600&output=webp';";
  }
  return "this.onerror=null;this.src='"+svgPack(p)+"'";
}
/* procedural SVG packshot fallback — brand-consistent tub silhouette */
function svgPack(p){
  const t = (p.t||"").slice(0,22);
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 300 300'>
<rect width='300' height='300' fill='%23F4F2ED'/>
<rect x='95' y='70' width='110' height='160' rx='14' fill='%23EDE9E0' stroke='%23D9D4C8'/>
<rect x='88' y='58' width='124' height='26' rx='8' fill='%23141414'/>
<rect x='105' y='108' width='90' height='84' rx='6' fill='%23ffffff' stroke='%23E4E1DA'/>
<text x='150' y='150' font-family='Archivo,Arial' font-weight='900' font-size='15' fill='%230A0A0A' text-anchor='middle'>LIMITLESS</text>
<text x='150' y='172' font-family='Arial' font-size='9' fill='%235A5A57' text-anchor='middle'>${esc(t).replace(/'/g,'')}</text>
<rect x='118' y='205' width='64' height='6' rx='3' fill='%23FF6A00'/>
</svg>`;
  return "data:image/svg+xml," + encodeURIComponent(svg).replace(/'/g,'%27');
}

/* ===================== FILTER + SORT ===================== */
function filtered(){
  let list = PRODUCTS.slice();
  if(state.wishOnly) list = list.filter(p => wishlist.has(p.c));
  if(state.cat) list = list.filter(p => p.k === state.cat);
  if(state.goal){ const ks = CATS.filter(c=>c.g===state.goal).map(c=>c.k); list = list.filter(p=>ks.includes(p.k)); }
  if(state.q){
    const q = state.q.toLowerCase();
    list = list.filter(p => (p.t||"").toLowerCase().includes(q) || (catName[p.k]||"").toLowerCase().includes(q) || (p.c||"").toLowerCase().includes(q));
  }
  const s = state.sort;
  if(s==="terlaris") list.sort((a,b)=>(b.q||0)-(a.q||0));
  else if(s==="harga-asc") list.sort((a,b)=>(a.price==null?Infinity:a.price)-(b.price==null?Infinity:b.price));
  else if(s==="harga-desc") list.sort((a,b)=>(b.price==null?-1:b.price)-(a.price==null?-1:a.price));
  else if(s==="az") list.sort((a,b)=>(a.t||"").localeCompare(b.t||""));
  return list;
}

/* ===================== RENDER: CARD ===================== */
function cardHtml(p){
  const d = discPct(p);
  const benefits = BENEFITS.map(b=>`<li><svg viewBox="0 0 24 24" fill="none" stroke="#2FA968" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>${esc(b)}</li>`).join("");
  return `<article class="card" data-c="${p.c}">
    <div class="media" onclick="openQuick('${p.c}')">
      ${d?`<span class="tag-disc">-${d}%</span>`:""}
      <button class="heart ${wishlist.has(p.c)?'on':''}" onclick="event.stopPropagation();toggleWish('${p.c}')" aria-label="Favorit">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 1 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>
      </button>
      <img loading="lazy" src="${img(p)}" alt="${esc(p.t)}" onerror="${imgFallback(p)}">
    </div>
    <div class="body">
      <span class="cat">${esc(catName[p.k]||p.k||"")}</span>
      <span class="title" onclick="openQuick('${p.c}')">${esc(p.t)}</span>
      <ul class="benefits">${benefits}</ul>
      <div class="price-row">${priceHtml(p)}</div>
      <button class="btn block add" onclick="addToCart('${p.c}',1)">Tambah</button>
    </div>
  </article>`;
}
function railCardHtml(p){
  return `<article class="card" data-c="${p.c}">
    <div class="media" onclick="openQuick('${p.c}')">
      <button class="heart ${wishlist.has(p.c)?'on':''}" onclick="event.stopPropagation();toggleWish('${p.c}')" aria-label="Favorit">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 1 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>
      </button>
      <img loading="lazy" src="${img(p)}" alt="${esc(p.t)}" onerror="${imgFallback(p)}">
    </div>
    <div class="body">
      <span class="cat">${esc(catName[p.k]||"")}</span>
      <span class="title" onclick="openQuick('${p.c}')">${esc(p.t)}</span>
      <div class="price-row">${priceHtml(p)}</div>
      <button class="btn block add" onclick="addToCart('${p.c}',1)">Tambah</button>
    </div>
  </article>`;
}

/* ===================== RENDER: GRID ===================== */
function renderGrid(){
  const list = filtered();
  const grid = document.getElementById("grid");
  const shown = list.slice(0, state.page*PAGE);
  grid.innerHTML = shown.map(cardHtml).join("") || `<div class="empty-state" style="grid-column:1/-1">Tidak ada produk yang cocok.<br><button class="btn bone" style="margin-top:14px" onclick="resetFilters()">Reset Filter</button></div>`;
  document.getElementById("countNote").textContent = list.length + " produk" + (state.cat?(" · "+ (catName[state.cat]||"")):"") + (state.wishOnly?" · Favorit":"");
  document.getElementById("loadMoreWrap").style.display = shown.length < list.length ? "flex" : "none";
  const goalName = state.goal ? ((GOALS.find(x=>x.g===state.goal)||{}).n||"Produk") : "";
  document.getElementById("gridTitle").textContent = state.wishOnly ? "Favorit Saya" : (goalName || (state.cat ? (catName[state.cat]||"Produk") : (state.q?('Hasil: "'+state.q+'"'):"Semua Produk")));
}
function loadMore(){ state.page++; renderGrid(); }
function resetFilters(){ state = {cat:"",q:"",sort:"relevan",wishOnly:false,goal:"",page:1}; document.getElementById("searchInput").value=""; document.getElementById("sortSel").value="relevan"; syncChips(); renderGrid(); }

/* ===================== FILTER ACTIONS ===================== */
function filterByCat(k){ state.cat=k; state.goal=""; state.wishOnly=false; state.page=1; syncChips(); renderGrid(); }
function filterByGoal(g){ state.goal=g; state.cat=""; state.wishOnly=false; state.q=""; state.page=1; document.getElementById("searchInput").value=""; syncChips(); renderGrid(); }
function setSort(s){ state.sort=s; state.page=1; document.getElementById("sortSel").value=s; renderGrid(); }
function toggleWishlistFilter(){ state.wishOnly=!state.wishOnly; state.page=1; if(state.wishOnly){state.cat="";} renderGrid(); scrollToGrid(); syncChips(); }
function syncChips(){
  document.querySelectorAll("#chips .chip").forEach(c=>c.classList.toggle("on", c.dataset.k===state.cat && !state.wishOnly));
  document.getElementById("chipAll")?.classList.toggle("on", !state.cat && !state.wishOnly);
}

/* ===================== SEARCH ===================== */
let searchT;
function onSearch(v){
  clearTimeout(searchT);
  const box = document.getElementById("suggest");
  const q = v.trim().toLowerCase();
  if(!q){ box.classList.remove("open"); state.q=""; state.page=1; renderGrid(); return; }
  searchT = setTimeout(()=>{
    const hits = PRODUCTS.filter(p=>(p.t||"").toLowerCase().includes(q)).slice(0,6);
    box.innerHTML = hits.map(p=>`<a onclick="openQuick('${p.c}')">
      <img loading="lazy" src="${img(p)}" alt="" onerror="${imgFallback(p)}">
      <span><span class="st">${esc(p.t)}</span><br><span class="sc">${esc(catName[p.k]||"")} · ${p.price!=null?money(p.price):'Chat harga'}</span></span></a>`).join("")
      || `<div style="padding:14px;font-size:13px;color:var(--muted)">Tidak ditemukan. <a onclick="runSearch('${esc(q)}')" style="text-decoration:underline">Cari semua</a></div>`;
    box.classList.add("open");
    state.q=v; state.page=1; renderGrid();
  },120);
}
function runSearch(q){ document.getElementById("searchInput").value=q; state.q=q; state.page=1; document.getElementById("suggest").classList.remove("open"); renderGrid(); scrollToGrid(); }
function focusSearch(){ const el=document.getElementById("searchInput"); if(el.offsetParent){el.focus();} else { const q=prompt("Cari produk:"); if(q){runSearch(q);} } }

/* ===================== WISHLIST ===================== */
function toggleWish(c){
  if(wishlist.has(c)) wishlist.delete(c); else { wishlist.add(c); toast("Ditambah ke favorit"); }
  document.querySelectorAll(`[data-c="${c}"] .heart`).forEach(h=>h.classList.toggle("on", wishlist.has(c)));
  updateBadges(); if(state.wishOnly) renderGrid();
}

/* ===================== CART ===================== */
function addToCart(c, qty){
  cart[c] = (cart[c]||0) + (qty||1);
  updateBadges(); renderCart(); toast("Ditambah ke keranjang"); track("add_to_cart", c);
}
function changeQty(c, delta){
  cart[c] = (cart[c]||0) + delta;
  if(cart[c] <= 0) delete cart[c];
  updateBadges(); renderCart();
}
function removeFromCart(c){ delete cart[c]; updateBadges(); renderCart(); }
function cartCount(){ return Object.values(cart).reduce((a,b)=>a+b,0); }
function cartSubtotal(){
  let sum=0, hasUnpriced=false;
  for(const c in cart){ const p=byCode[c]; if(p && p.price!=null) sum += p.price*cart[c]; else hasUnpriced=true; }
  return {sum, hasUnpriced};
}
function renderCart(){
  const body = document.getElementById("cartBody");
  const foot = document.getElementById("cartFoot");
  const codes = Object.keys(cart);
  if(!codes.length){
    body.innerHTML = `<div class="empty-state"><svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:.4;margin:0 auto 12px"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.7 13.4a2 2 0 0 0 2 1.6h9.7a2 2 0 0 0 2-1.6L23 6H6"/></svg><p>Keranjang masih kosong.</p><button class="btn bone" style="margin-top:14px" onclick="closeAll();scrollToGrid()">Mulai Belanja</button></div>`;
    foot.innerHTML = ""; return;
  }
  body.innerHTML = codes.map(c=>{
    const p = byCode[c]; if(!p) return "";
    const line = p.price!=null ? money(p.price*cart[c]) : "Chat harga";
    return `<div class="cart-line">
      <img class="thumb" loading="lazy" src="${img(p)}" alt="" onerror="${imgFallback(p)}">
      <div><div class="ct">${esc(p.t)}</div><div class="cc">${esc(p.c)} · ${esc(catName[p.k]||"")}</div>
        <div class="qty" style="margin-top:8px"><button onclick="changeQty('${c}',-1)">−</button><span>${cart[c]}</span><button onclick="changeQty('${c}',1)">+</button></div>
      </div>
      <div style="text-align:right"><div style="font-family:Archivo;font-weight:900;font-size:14px">${line}</div>
        <div class="rm" onclick="removeFromCart('${c}')">Hapus</div></div>
    </div>`;
  }).join("");

  const {sum, hasUnpriced} = cartSubtotal();
  const branchOpts = CONFIG.branches.map((b,i)=>`<option value="${i}">${esc(b.n)}</option>`).join("");
  const courierOpts = CONFIG.couriers.map(x=>`<option>${esc(x)}</option>`).join("");
  foot.innerHTML = `
    <div class="fulfill">
      <span class="label muted">Pengiriman</span>
      <div class="seg">
        <button class="${fulfillMode==='kirim'?'on':''}" onclick="setFulfill('kirim')">🛵 Dikirim</button>
        <button class="${fulfillMode==='ambil'?'on':''}" onclick="setFulfill('ambil')">🏬 Ambil di Cabang</button>
      </div>
      ${fulfillMode==='kirim'
        ? `<select id="courierSel" aria-label="Kurir">${courierOpts}</select>`
        : `<select id="branchSel" aria-label="Cabang">${branchOpts}</select>`}
    </div>
    <div class="subtotal"><span>Subtotal</span><span>${sum>0?money(sum):'—'}</span></div>
    ${hasUnpriced?'<div class="muted" style="font-size:12px">*Sebagian item belum berharga — admin akan konfirmasi total via WhatsApp.</div>':''}
    <button class="btn wa block" onclick="checkout()">Pesan via WhatsApp</button>
    ${CONFIG.payEndpoint?'<button class="btn block" onclick="payOnline()">Bayar Online (QRIS/VA)</button>':''}
    <div style="display:flex;flex-wrap:wrap;gap:5px;justify-content:center;margin-top:2px">${PAY_BADGES.map(b=>`<span class="pill" style="font-size:10.5px;padding:4px 9px">${b}</span>`).join("")}</div>`;
}
function setFulfill(m){ fulfillMode=m; renderCart(); }

/* ===================== CHECKOUT (WhatsApp, branch-aware) ===================== */
function pickAdmin(){ return CONFIG.waAdmins[Math.floor(Math.random()*CONFIG.waAdmins.length)]; }
function buildOrderMessage(){
  const codes = Object.keys(cart);
  let lines = [`Halo *${CONFIG.brand}* 👋`, "Saya mau pesan:", ""];
  codes.forEach((c,idx)=>{
    const p=byCode[c]; if(!p) return;
    const price = p.price!=null ? (" — "+money(p.price*cart[c])) : " — (chat harga)";
    lines.push(`${idx+1}. ${cart[c]}x ${p.t} [${p.c}]${price}`);
  });
  const {sum, hasUnpriced} = cartSubtotal();
  lines.push("");
  if(sum>0) lines.push(`*Subtotal: ${money(sum)}*${hasUnpriced?' (+ item chat harga)':''}`);
  // fulfillment line
  let dest;
  if(fulfillMode==='ambil'){
    const i = parseInt((document.getElementById("branchSel")||{}).value || "0",10);
    const b = CONFIG.branches[i] || CONFIG.branches[0];
    lines.push(`🏬 Ambil di Cabang: ${b.n}${b.a?(" — "+b.a):""}`);
    dest = (b.wa && b.wa.trim()) ? b.wa.trim() : pickAdmin();   // route to branch WA when set
  } else {
    const courier = (document.getElementById("courierSel")||{}).value || CONFIG.couriers[0];
    lines.push(`🛵 Dikirim via: ${courier}`);
    dest = pickAdmin();                                          // delivery -> random admin pool
  }
  lines.push("", "Mohon konfirmasi ketersediaan & ongkir ya 🙏");
  return {text:lines.join("\n"), dest};
}
function checkout(){
  if(!cartCount()){ toast("Keranjang masih kosong"); return; }
  const {text, dest} = buildOrderMessage();
  track("begin_checkout");
  window.open("https://wa.me/"+dest+"?text="+enc(text), "_blank");
}
function waConsult(){
  const dest = pickAdmin();
  const text = `Halo *${CONFIG.brand}* 👋 saya mau konsultasi produk suplemen.`;
  window.open("https://wa.me/"+dest+"?text="+enc(text), "_blank");
}

/* ===================== PAYMENT GATEWAY HOOK (single integration point) ===================== */
async function payOnline(){
  if(!CONFIG.payEndpoint){ checkout(); return; }           // not configured -> WhatsApp fallback
  const items = Object.keys(cart).map(c=>({code:c, name:byCode[c]?.t, qty:cart[c], price:byCode[c]?.price ?? null}));
  const {sum} = cartSubtotal();
  try{
    track("begin_checkout");
    const res = await fetch(CONFIG.payEndpoint, {
      method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({brand:CONFIG.brand, items, subtotal:sum, fulfillment:fulfillMode})
    });
    const data = await res.json();
    if(data && data.invoiceUrl){ window.location.href = data.invoiceUrl; }   // gateway returns invoice -> redirect
    else { toast("Gagal membuat invoice, lanjut via WhatsApp"); checkout(); }
  }catch(e){ toast("Koneksi gateway gagal, lanjut via WhatsApp"); checkout(); }
}

/* ===================== QUICK VIEW ===================== */
let QV_QTY = 1;
function openQuick(c){
  const p = byCode[c]; if(!p) return;
  QV_QTY = 1;
  pushRecent(c);
  location.hash = "p=" + c;                                  // shareable deep link
  document.getElementById("suggest").classList.remove("open");
  const related = PRODUCTS.filter(x=>x.k===p.k && x.c!==c).sort((a,b)=>(b.q||0)-(a.q||0)).slice(0,4);
  const card = document.getElementById("qvCard");
  card.innerHTML = `
    <button class="iconbtn close-x qv-close" onclick="closeQuick()">✕</button>
    <div class="qv-media"><img loading="lazy" src="${img(p)}" alt="${esc(p.t)}" onerror="${imgFallback(p)}"></div>
    <div class="qv-info">
      <span class="cat">${esc(catName[p.k]||"")}</span>
      <h2>${esc(p.t)}</h2>
      <div class="qv-price">${priceHtml(p,true)}</div>
      <ul class="benefits" style="margin:6px 0 0">${BENEFITS.map(b=>`<li><svg viewBox="0 0 24 24" fill="none" stroke="#2FA968" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>${esc(b)}</li>`).join("")}</ul>
      <div style="margin:18px 0 6px"><span class="label muted">Jumlah</span></div>
      <div class="qty"><button onclick="qvQty(-1)">−</button><span id="qvQty">1</span><button onclick="qvQty(1)">+</button></div>
      <div class="qv-actions">
        <button class="btn" style="flex:1" onclick="addToCart('${p.c}',document.getElementById('qvQty')?+document.getElementById('qvQty').textContent:1);closeQuick()">Tambah ke Keranjang</button>
        <button class="btn ghost" onclick="toggleWish('${p.c}')">♥ Favorit</button>
      </div>
      <button class="btn bone block" onclick="shareProduct('${p.c}')">Bagikan via WhatsApp</button>
      <p class="muted" style="font-size:12px;margin-top:14px">Kode: ${esc(p.c)} · COD se-Indonesia · Garansi 30 hari</p>
    </div>
    ${related.length?`<div class="qv-related"><h4>Produk Terkait</h4><div class="grid" style="grid-template-columns:repeat(4,1fr)">${related.map(railCardHtml).join("")}</div></div>`:""}`;
  document.getElementById("qv").classList.add("open");
  document.getElementById("scrim").classList.add("open");
  document.body.style.overflow="hidden";
  injectProductJsonLd(p);
  track("view_item", c);
}
function qvQty(d){ const el=document.getElementById("qvQty"); let v=Math.max(1,(+el.textContent)+d); el.textContent=v; }
function closeQuick(){
  document.getElementById("qv").classList.remove("open");
  if(!anyDrawerOpen()) document.getElementById("scrim").classList.remove("open");
  document.body.style.overflow="";
  if(location.hash.indexOf("p=")>-1) history.replaceState(null,"",location.pathname+location.search);
}
function shareProduct(c){
  const p=byCode[c]; if(!p) return;
  const url = location.origin+location.pathname+"#p="+c;
  const text = `Cek produk ini di *${CONFIG.brand}*:\n${p.t}${p.price!=null?(" — "+money(p.price)):""}\n${url}`;
  window.open("https://wa.me/?text="+enc(text), "_blank");
}

/* ===================== RECENTLY VIEWED ===================== */
function pushRecent(c){
  recent = recent.filter(x=>x!==c); recent.unshift(c); recent = recent.slice(0,12);
  const sec=document.getElementById("recentSec");
  const rail=document.getElementById("recentRail");
  const items = recent.map(x=>byCode[x]).filter(Boolean);
  if(items.length){ sec.style.display="block"; rail.innerHTML = items.map(railCardHtml).join(""); }
}

/* ===================== BADGES / UI SYNC ===================== */
function updateBadges(){
  const cc = cartCount(), wc = wishlist.size;
  ["cartBadge","cartTabBadge"].forEach(id=>{const e=document.getElementById(id); e.style.display=cc?"flex":"none"; e.textContent=cc;});
  ["wishBadge","favTabBadge"].forEach(id=>{const e=document.getElementById(id); e.style.display=wc?"flex":"none"; e.textContent=wc;});
}

/* ===================== DRAWERS / MENUS ===================== */
function openDrawer(id){ closeMega(); document.getElementById(id).classList.add("open"); document.getElementById("scrim").classList.add("open"); document.body.style.overflow="hidden"; if(id==="cart")renderCart(); }
function anyDrawerOpen(){ return [...document.querySelectorAll(".drawer")].some(d=>d.classList.contains("open")); }
function closeAll(){
  document.querySelectorAll(".drawer").forEach(d=>d.classList.remove("open"));
  document.getElementById("qv").classList.remove("open");
  closeMega();
  document.getElementById("scrim").classList.remove("open");
  document.body.style.overflow="";
}
let openMegaId=null;
function toggleMega(which){
  const id="mega-"+which;
  if(openMegaId===id){ closeMega(); return; }
  closeMega();
  document.getElementById(id).classList.add("open");
  openMegaId=id;
}
function closeMega(){ document.querySelectorAll(".mega").forEach(m=>m.classList.remove("open")); openMegaId=null; }
document.addEventListener("click",e=>{
  if(!e.target.closest(".mega") && !e.target.closest(".nav-links") && !e.target.closest("#tab-cat")) closeMega();
  if(!e.target.closest(".nav-search")) document.getElementById("suggest").classList.remove("open");
});

/* ===================== NAV HELPERS ===================== */
function goHome(){ closeAll(); resetFilters(); window.scrollTo({top:0,behavior:"smooth"}); }
function scrollToGrid(){ closeAll(); document.getElementById("shop").scrollIntoView({behavior:"smooth",block:"start"}); }

/* ===================== TOAST ===================== */
let toastT;
function toast(msg){
  const t=document.getElementById("toast"); t.textContent=msg; t.classList.add("show");
  clearTimeout(toastT); toastT=setTimeout(()=>t.classList.remove("show"),1800);
}

/* ===================== SEO: JSON-LD ===================== */
function injectProductJsonLd(p){
  let el=document.getElementById("ld-product"); if(el) el.remove();
  const data = {
    "@context":"https://schema.org","@type":"Product",
    "name":p.t, "sku":p.c, "category":catName[p.k]||p.k,
    "brand":{"@type":"Brand","name":CONFIG.brand},
    "image": CLEAN_BUILD? (location.origin+location.pathname.replace(/[^/]*$/,'')+"images_clean/"+p.c+".webp") : (p.i||undefined)
  };
  if(p.price!=null){
    data.offers={"@type":"Offer","priceCurrency":"IDR","price":p.price,"availability":"https://schema.org/InStock",
      "url":location.origin+location.pathname+"#p="+p.c};
  }
  const bc = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
    {"@type":"ListItem","position":1,"name":"Beranda","item":location.origin+location.pathname},
    {"@type":"ListItem","position":2,"name":catName[p.k]||"Produk"},
    {"@type":"ListItem","position":3,"name":p.t}
  ]};
  el=document.createElement("script"); el.type="application/ld+json"; el.id="ld-product";
  el.textContent=JSON.stringify([data,bc]); document.head.appendChild(el);
  // Open Graph product tags
  setMeta("og:title", p.t+" — "+CONFIG.brand);
  if(p.price!=null){ setMeta("product:price:amount", p.price); setMeta("product:price:currency","IDR"); }
}
function setMeta(prop,val){
  let m=document.querySelector(`meta[property="${prop}"]`);
  if(!m){ m=document.createElement("meta"); m.setAttribute("property",prop); document.head.appendChild(m); }
  m.setAttribute("content",val);
}

/* ===================== ANALYTICS HOOK ===================== */
function initAnalytics(){
  const id=CONFIG.analyticsId; if(!id) return;            // empty -> inject nothing
  if(/^G-/.test(id)){
    const s=document.createElement("script"); s.async=true; s.src="https://www.googletagmanager.com/gtag/js?id="+id; document.head.appendChild(s);
    window.dataLayer=window.dataLayer||[]; window.gtag=function(){dataLayer.push(arguments)}; gtag('js',new Date()); gtag('config',id);
  } else {
    // treat as Meta Pixel ID
    !function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');
    fbq('init',id); fbq('track','PageView');
  }
}
function track(ev, code){
  if(!CONFIG.analyticsId) return;
  const p = code?byCode[code]:null;
  if(window.gtag) gtag('event', ev, p?{items:[{item_id:p.c,item_name:p.t,price:p.price||0}]}:{});
  if(window.fbq){ const map={view_item:'ViewContent',add_to_cart:'AddToCart',begin_checkout:'InitiateCheckout'}; if(map[ev]) fbq('track',map[ev], p?{content_ids:[p.c],value:p.price||0,currency:'IDR'}:{}); }
}

/* ===================== HASH ROUTING ===================== */
function handleHash(){
  const m = location.hash.match(/p=([^&]+)/);
  if(m && byCode[m[1]]) openQuick(m[1]);
}
window.addEventListener("hashchange", ()=>{ if(!location.hash.includes("p=")) closeQuick(); else handleHash(); });

/* ===================== STATIC RENDERS ===================== */
function buildStatic(){
  // hero trust + strip
  const tIco = {Original:"✓","BPOM":"🛡","Halal MUI":"☪","COD":"📦","Gratis Ongkir":"🚚","Garansi 30 Hari":"↩"};
  document.getElementById("heroTrust").innerHTML = CONFIG.trust.map(t=>`<span class="pill">${tIco[t]||"✓"} ${esc(t)}</span>`).join("");
  document.getElementById("trustStrip").innerHTML = CONFIG.trust.map(t=>`<span>${tIco[t]||"✓"} ${esc(t)}</span>`).join("");

  // chips
  const chips = [`<button class="chip on" id="chipAll" onclick="filterByCat('')">Semua</button>`]
    .concat(CATS.filter(c=>c.count).map(c=>`<button class="chip" data-k="${c.k}" onclick="filterByCat('${c.k}')">${esc(c.n)} (${c.count})</button>`));
  document.getElementById("chips").innerHTML = chips.join("");

  // mega cats + quick + goals
  document.getElementById("megaCats").innerHTML = CATS.filter(c=>c.count).map(c=>`<button onclick="filterByCat('${c.k}');closeMega();scrollToGrid()"><span class="cn">${esc(c.n)}</span><span class="cc">${c.count}</span></button>`).join("");
  document.getElementById("megaQuick").innerHTML = ["Whey","Creatine","Pre-Workout","Vitamin","Mass Gainer","BCAA"].map(q=>`<button class="pill" onclick="runSearch('${q}');closeMega()">${q}</button>`).join("");
  document.getElementById("megaGoals").innerHTML = GOALS.map(g=>{
    const n = PRODUCTS.filter(p=>(CATS.find(c=>c.k===p.k)||{}).g===g.g).length;
    return `<button onclick="filterByGoal('${g.g}');closeMega();scrollToGrid()"><span class="cn">${esc(g.n)}</span><span class="cc">${n}</span></button>`;
  }).join("");

  // category showcase (first 8 non-empty)
  document.getElementById("catShow").innerHTML = CATS.filter(c=>c.count).slice(0,8).map(c=>`
    <button class="cat-tile" onclick="filterByCat('${c.k}');scrollToGrid()">
      <div><h3>${esc(c.n)}</h3><div class="cc">${c.count} produk</div></div><div class="arrow">→</div></button>`).join("");

  // best sellers rail
  const best = PRODUCTS.slice().sort((a,b)=>(b.q||0)-(a.q||0)).slice(0,12);
  document.getElementById("bestRail").innerHTML = best.map(railCardHtml).join("");

  // footer
  document.getElementById("footCats").innerHTML = CATS.filter(c=>c.count).slice(0,6).map(c=>`<a href="#" onclick="filterByCat('${c.k}');scrollToGrid();return false">${esc(c.n)}</a>`).join("");
  document.getElementById("footPay").innerHTML = PAY_BADGES.map(b=>`<span>${b}</span>`).join("");
  document.getElementById("footBranches").innerHTML = CONFIG.branches.map(b=>`<a href="#" onclick="${b.wa?`window.open('https://wa.me/${b.wa}','_blank')`:'waConsult()'};return false">${esc(b.n)}${b.a?`<br><span class='muted' style='font-size:11px'>${esc(b.a)}</span>`:''}</a>`).join("");

  // mobile nav
  document.getElementById("mnav").innerHTML =
    `<button onclick="goHome()">Beranda</button>` +
    `<button onclick="setSort('terlaris');scrollToGrid()">Terlaris</button>` +
    `<button onclick="filterByCat('');scrollToGrid()">Semua Produk</button>` +
    CATS.filter(c=>c.count).map(c=>`<button onclick="filterByCat('${c.k}');scrollToGrid()">${esc(c.n)} <span class="muted">${c.count}</span></button>`).join("") +
    `<button onclick="waConsult()" style="color:var(--wa)">Chat Admin (WhatsApp)</button>`;
}
/* ===================== THREE.JS SIGNATURE TUB ===================== */
let tubAnim=true;
function initTub(){
  const canvas=document.getElementById("tub"); if(!canvas || !window.THREE) return;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const scene=new THREE.Scene();
  const cam=new THREE.PerspectiveCamera(35,1,0.1,100); cam.position.set(0,0.3,6);
  const r=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true});
  r.setPixelRatio(Math.min(window.devicePixelRatio||1,2));    // DPR capped at 2
  function size(){ const w=canvas.clientWidth||360; r.setSize(w,w,false); cam.aspect=1; cam.updateProjectionMatrix(); }
  size(); window.addEventListener("resize",size);

  scene.add(new THREE.AmbientLight(0xffffff,0.75));
  const key=new THREE.DirectionalLight(0xffffff,0.9); key.position.set(3,5,4); scene.add(key);
  const rim=new THREE.DirectionalLight(0xffffff,0.4); rim.position.set(-4,2,-3); scene.add(rim);

  const grp=new THREE.Group();
  const body=new THREE.Mesh(new THREE.CylinderGeometry(1.05,1.05,2.2,64),
    new THREE.MeshStandardMaterial({color:0xEDE9E0,roughness:0.55,metalness:0.05}));
  grp.add(body);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(1.12,1.12,0.5,64),
    new THREE.MeshStandardMaterial({color:0x141414,roughness:0.4}));
  cap.position.y=1.35; grp.add(cap);
  // canvas label "LIMITLESS"
  const lc=document.createElement("canvas"); lc.width=512; lc.height=256; const x=lc.getContext("2d");
  x.fillStyle="#ffffff"; x.fillRect(0,0,512,256);
  x.fillStyle="#0A0A0A"; x.font="900 86px Archivo, Arial"; x.textAlign="center";
  x.fillText("LIMITLESS",256,120);
  x.fillStyle="#FF6A00"; x.fillRect(150,150,212,14);
  x.fillStyle="#5A5A57"; x.font="600 30px Inter, Arial"; x.fillText("NUTRITION",256,205);
  const tex=new THREE.CanvasTexture(lc);
  const label=new THREE.Mesh(new THREE.CylinderGeometry(1.06,1.06,1.2,64,1,true),
    new THREE.MeshStandardMaterial({map:tex,roughness:0.5}));
  label.rotation.y=Math.PI; grp.add(label);
  scene.add(grp); grp.rotation.x=0.08;

  // drag to spin
  let drag=false,px=0,vel=0.005;
  const down=e=>{drag=true;px=(e.touches?e.touches[0].clientX:e.clientX);};
  const move=e=>{ if(!drag)return; const cx=(e.touches?e.touches[0].clientX:e.clientX); vel=(cx-px)*0.01; grp.rotation.y+=vel; px=cx; };
  const up=()=>drag=false;
  canvas.addEventListener("mousedown",down); window.addEventListener("mousemove",move); window.addEventListener("mouseup",up);
  canvas.addEventListener("touchstart",down,{passive:true}); window.addEventListener("touchmove",move,{passive:true}); window.addEventListener("touchend",up);

  function loop(){
    if(!tubAnim || document.hidden){ requestAnimationFrame(loop); return; } // pause on hidden
    if(!drag && !reduce){ grp.rotation.y+=0.005; }                          // auto-rotate (reduced-motion: off)
    r.render(scene,cam); requestAnimationFrame(loop);
  }
  if(reduce){ grp.rotation.y=-0.5; r.render(scene,cam); } else { loop(); }
}
document.addEventListener("visibilitychange",()=>{ tubAnim=!document.hidden; });

/* ===================== SCROLL UI (buybar, totop) ===================== */
function initBuybar(){
  const top = PRODUCTS.slice().sort((a,b)=>(b.q||0)-(a.q||0))[0];
  if(!top) return;
  BB_CODE = top.c;
  document.getElementById("bbTitle").textContent = "Terlaris: " + top.t;
  document.getElementById("bbPrice").textContent = top.price!=null ? money(top.price) : "Chat untuk harga";
}
window.addEventListener("scroll",()=>{
  const y=window.scrollY;
  document.getElementById("totop").classList.toggle("show", y>700);
  const shop=document.getElementById("shop");
  const r=shop.getBoundingClientRect();
  const inShop = r.top < window.innerHeight*0.5 && r.bottom > 200;   // featured buy-bar while browsing catalog
  document.getElementById("buybar").classList.toggle("show", inShop && !anyDrawerOpen());
},{passive:true});

document.addEventListener("keydown",e=>{ if(e.key==="Escape") closeAll(); });

/* ===================== INIT ===================== */
buildStatic();
renderGrid();
updateBadges();
initBuybar();
initAnalytics();
initTub();
handleHash();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
