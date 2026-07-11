# -*- coding: utf-8 -*-
"""資さんうどん 公式通販（sukesanstore.com）の冷凍商品 → sukesan_raw.json

店舗メニューの栄養成分は公式未公開のため、公式冷凍商品の栄養成分表示を
「参考値」として収集する（店舗品と完全一致ではない）。

商品一覧 /products/list.php から商品ページを辿り、
「栄養成分表示（1食376ｇ当たり）エネルギー516kcal、たんぱく質17ｇ、…」を抽出。
出力: data/sukesan_raw.json  [{name, basis, kcal, prot, salt}, ...]
"""
import json
import re
import time
import urllib.request
from pathlib import Path

LIST_URL = "https://sukesanstore.com/products/list.php"
OUT = Path(__file__).parent / "data" / "sukesan_raw.json"
WAIT = 0.5
# 食品以外（グッズ・ギフト等）と重複セットを除外
EXCLUDE = re.compile(r"^(goods-|nikoand_|siawase_|26ochugen|25teiki|25otamesiset|udon-set)")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read().decode("utf-8", errors="replace")


def to_half(s):
    return s.translate(str.maketrans("０１２３４５６７８９．ｇ", "0123456789.g"))


NUTRI_RE = re.compile(
    r"栄養成分表示[（(]([^）)]{1,25})[）)][：:\s]*"
    r"エネルギー\s*([\d.]+)\s*kcal[、,]\s*"
    r"(?:たんぱく質|タンパク質|たん白質)\s*([\d.]+)\s*g[、,]\s*"
    r"脂質\s*[\d.]+\s*g[、,]\s*"
    r"炭水化物\s*[\d.]+\s*g[、,]\s*"
    r"食塩相当量\s*([\d.]+)\s*g"
)
TITLE_RE = re.compile(r"<title>([^<]+)</title>")


def clean_title(t):
    # 「資さんうどん」「｜以降のサイト名」などを除去
    t = re.sub(r"[｜|].*$", "", t).strip()
    t = re.sub(r"^【?\s*資さんうどん\s*】?", "", t).strip()
    return t


def main():
    html = fetch(LIST_URL)
    slugs = sorted(set(re.findall(r'/products/([a-zA-Z0-9_\-]+)/', html)))
    slugs = [s for s in slugs if not EXCLUDE.match(s)]
    print(f"target products: {slugs}")

    items, seen_values = [], set()
    for slug in slugs:
        time.sleep(WAIT)
        try:
            raw = fetch(f"https://sukesanstore.com/products/{slug}/")
        except Exception as e:
            print(f"  skip {slug}: {e}")
            continue
        # <title>はタグ除去前に取得し、本文はタグを外して連続テキスト化
        title_html = TITLE_RE.search(raw)
        page = to_half(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)))
        matches = NUTRI_RE.findall(page)
        if len(matches) != 1:
            print(f"  skip {slug}: 栄養成分表示 {len(matches)}件")
            continue
        basis, kcal, prot, salt = matches[0]
        name = clean_title(title_html.group(1)) if title_html else slug
        key = (kcal, prot, salt)  # 3食/5食パック等の重複を排除
        if key in seen_values:
            continue
        seen_values.add(key)
        items.append({
            "name": name, "basis": basis.replace("当たり", "").replace("当り", "").strip(),
            "kcal": float(kcal), "prot": float(prot), "salt": float(salt),
        })
        print(f"  {name}: {basis} {kcal}kcal 塩{salt}g")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"sukesan: {len(items)} items -> {OUT.name}")


if __name__ == "__main__":
    main()
