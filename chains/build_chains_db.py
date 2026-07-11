# -*- coding: utf-8 -*-
"""3社の収集結果 → app/chains.json

items の各要素: [名前, カテゴリ, kcal, たんぱく質g, 食塩g, 基準量表示]
値が不明（未公開）のものは null。
"""
import json
import re
from datetime import date
from pathlib import Path

BASE = Path(__file__).parent
DATA = BASE / "data"
OUT = BASE.parent / "docs" / "chains.json"


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def clean_sukesan_name(name):
    """通販パック表記（3人前・2パック等）を除去して店舗メニュー風の名前に"""
    name = re.sub(r"[　\s]*[0-9０-９]+(人前|パック|袋|食)", "", name)
    return name.strip("　 ")


def main():
    joyfull = [[i["name"], i["cat"], i["kcal"], i["prot"], i["salt"], None]
               for i in load("joyfull_raw.json")]
    komeda = [[i["name"], i["cat"], i["kcal"], None, None, None]
              for i in load("komeda_raw.json")]
    sukesan = [[clean_sukesan_name(i["name"]), "", i["kcal"], i["prot"], i["salt"], i["basis"]]
               for i in load("sukesan_raw.json")]

    db = {
        "updated": date.today().isoformat(),
        "chains": [
            {"id": "joyfull", "name": "ジョイフル",
             "note": "公式の栄養成分一覧（目安値）に基づく",
             "items": joyfull},
            {"id": "komeda", "name": "コメダ珈琲店",
             "note": "公式公開はカロリーのみ。食塩・たんぱく質は不明（集計に含まれません）",
             "items": komeda},
            {"id": "sukesan", "name": "資さんうどん",
             "note": "公式冷凍商品の表示に基づく参考値（店舗品と完全一致ではありません）",
             "items": sukesan},
        ],
    }
    OUT.write_text(json.dumps(db, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    total = sum(len(c["items"]) for c in db["chains"])
    print(f"chains.json: {total} items "
          f"(joyfull {len(joyfull)} / komeda {len(komeda)} / sukesan {len(sukesan)}) "
          f"{OUT.stat().st_size/1024:.0f} KB")


if __name__ == "__main__":
    main()
