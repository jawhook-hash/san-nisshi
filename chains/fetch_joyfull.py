# -*- coding: utf-8 -*-
"""ジョイフル公式PDF（商品情報一覧）→ joyfull_raw.json

入力: ../raw/joyfull_cal.pdf（https://files.joyfull.co.jp/uploads/common/cal.pdf）
出力: data/joyfull_raw.json  [{name, cat, kcal, prot, salt}, ...]

PDFの表: メニュー名 | kcal | たんぱく質 | 脂質 | 炭水化物 | 食塩相当量 | アレルゲン28列
カテゴリ行は名前だけで数値が空。
"""
import json
import pdfplumber
from pathlib import Path

BASE = Path(__file__).parent
SRC = BASE.parent / "raw" / "joyfull_cal.pdf"
OUT = BASE / "data" / "joyfull_raw.json"


def parse_num(s):
    if s is None:
        return None
    s = str(s).replace(",", "").replace("\n", "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def main():
    items = []
    cat = ""
    with pdfplumber.open(SRC) as pdf:
        for page in pdf.pages[1:]:  # 1ページ目は注意書き
            for table in page.extract_tables():
                for row in table:
                    if not row or row[0] is None:
                        continue
                    name = str(row[0]).replace("\n", "").strip()
                    if not name or name == "メニュー名":
                        continue
                    kcal = parse_num(row[1]) if len(row) > 1 else None
                    if kcal is None:  # 数値なし＝カテゴリ見出し行
                        cat = name
                        continue
                    items.append({
                        "name": name,
                        "cat": cat,
                        "kcal": kcal,
                        "prot": parse_num(row[2]),
                        "salt": parse_num(row[5]),
                    })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"joyfull: {len(items)} items -> {OUT.name}")


if __name__ == "__main__":
    main()
