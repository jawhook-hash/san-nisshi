# -*- coding: utf-8 -*-
"""日本食品標準成分表（八訂）増補2023年 Excel → アプリ用 foods.json 変換

入力: raw/seibunhyo_honhyo.xlsx（文科省「第2章 本表データ」）
出力: app/foods.json
  形式: {"source": "...", "foods": [[食品番号, 食品名, kcal, たんぱく質g, 食塩g, カリウムmg, リンmg, 読み仮名], ...]}
  数値は可食部100gあたり。未測定(-)は null、微量(Tr)・推定値(かっこ)は数値化。
  読み仮名は pykakasi による自動生成（ひらがな検索用）。
"""
import json
import re
import openpyxl
import pykakasi
from pathlib import Path

BASE = Path(__file__).parent
SRC = BASE / "raw" / "seibunhyo_honhyo.xlsx"
OUT = BASE / "docs" / "foods.json"

SHEET = "表全体"
DATA_START_ROW = 13
# 列位置（1始まり）: 食品番号, 食品名, ENERC_KCAL, PROT-, K, P, NACL_EQ
COL_CODE, COL_NAME, COL_KCAL, COL_PROT, COL_K, COL_P, COL_NACL = 2, 4, 7, 10, 25, 28, 61


def parse_value(v):
    """成分値の表記ゆれを数値化。未測定(-)や不明は None。"""
    if v is None:
        return None
    s = str(v).strip().strip("()")  # 推定値のかっこは外して採用
    if s in ("-", "", "*"):
        return None
    if s == "Tr":
        return 0
    try:
        n = float(s)
    except ValueError:
        return None
    return int(n) if n == int(n) else round(n, 2)


def clean_name(name):
    """食品名の改行・連続空白を整理（区切りの全角スペースは1つ残す）"""
    return "　".join(part for part in str(name).replace("\n", "　").split("　") if part)


_kks = pykakasi.kakasi()

def to_yomi(name):
    """食品名の読み仮名（ひらがな）を生成。記号・かっこ類は除去"""
    plain = re.sub(r"[＜＞（）［］()<>\[\]　\s]", "", name)
    return "".join(item["hira"] for item in _kks.convert(plain))


def main():
    wb = openpyxl.load_workbook(SRC, read_only=True)
    ws = wb[SHEET]

    foods = []
    for row in ws.iter_rows(min_row=DATA_START_ROW, values_only=True):
        code, name = row[COL_CODE - 1], row[COL_NAME - 1]
        if code is None or name is None:
            continue
        cname = clean_name(name)
        foods.append([
            str(code),
            cname,
            parse_value(row[COL_KCAL - 1]),
            parse_value(row[COL_PROT - 1]),
            parse_value(row[COL_NACL - 1]),
            parse_value(row[COL_K - 1]),
            parse_value(row[COL_P - 1]),
            to_yomi(cname),
        ])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    db = {
        "source": "日本食品標準成分表（八訂）増補2023年（文部科学省）",
        "unit": "per100g",
        "columns": ["code", "name", "kcal", "protein_g", "salt_g", "potassium_mg", "phosphorus_mg", "yomi"],
        "foods": foods,
    }
    OUT.write_text(json.dumps(db, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    size_kb = OUT.stat().st_size / 1024
    print(f"foods: {len(foods)} items -> {OUT.name} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
