# -*- coding: utf-8 -*-
"""コメダ珈琲店 公式API → komeda_raw.json

API: https://eu.komeda.co.jp
  /v1/hp/menu-meta-data?brand_type=1   … カテゴリ定義（large_type）
  /v1/hp/menu?brand_type=1&category=X  … カテゴリ別メニュー一覧
  /v1/hp/menu-allergy/{id}             … カロリー（calori）とアレルゲン

公式に公開されている栄養成分はカロリーのみ（食塩・たんぱく質は非公開）。
出力: data/komeda_raw.json  [{name, cat, kcal}, ...]
"""
import json
import time
import urllib.request
from pathlib import Path

BASE_URL = "https://eu.komeda.co.jp/v1/hp"
OUT = Path(__file__).parent / "data" / "komeda_raw.json"
WAIT = 0.3  # サーバー負荷への配慮


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


def main():
    meta = get_json(f"{BASE_URL}/menu-meta-data?brand_type=1")
    cats = {}
    for field in meta["constant"]["fields"]:
        if field["name"] == "large_type":
            for v in field["values"]:
                if v["id"].startswith("1-"):  # コメダ珈琲店の実カテゴリのみ
                    cats[v["id"]] = v["display_name"]
    print(f"categories: {cats}")

    seen = {}
    for cat_id, cat_name in cats.items():
        time.sleep(WAIT)
        data = get_json(f"{BASE_URL}/menu?brand_type=1&category={cat_id}")
        for m in data.get("menus", []):
            if m.get("is_hidden") or m["id"] in seen:
                continue
            seen[m["id"]] = {"name": m["name"].strip(), "cat": cat_name}
    print(f"menus: {len(seen)}")

    items = []
    for i, (mid, info) in enumerate(seen.items(), start=1):
        time.sleep(WAIT)
        try:
            al = get_json(f"{BASE_URL}/menu-allergy/{mid}")
        except Exception as e:
            print(f"  skip {mid} {info['name']}: {e}")
            continue
        kcal = al.get("calori")
        if kcal in (None, ""):
            continue
        try:
            kcal = float(kcal)
        except ValueError:
            continue
        items.append({"name": info["name"], "cat": info["cat"], "kcal": kcal})
        if i % 20 == 0:
            print(f"  {i}/{len(seen)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"komeda: {len(items)} items -> {OUT.name}")


if __name__ == "__main__":
    main()
