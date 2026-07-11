# -*- coding: utf-8 -*-
"""餐日誌のアイコン生成（青地・白の「餐」・角丸）

出力: app/icon-180.png / icon-192.png / icon-512.png
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

APP = Path(__file__).parent / "docs"
BG = (37, 99, 235)      # アプリのアクセント色 #2563eb
FG = (255, 255, 255)
FONT = r"C:\Windows\Fonts\YuGothB.ttc"  # 游ゴシック Bold


def make_icon(size, path, rounded):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    radius = int(size * 0.22) if rounded else 0
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BG)

    font = ImageFont.truetype(FONT, int(size * 0.62))
    bbox = draw.textbbox((0, 0), "餐", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), "餐", font=font, fill=FG)
    img.save(path)
    print(f"{path.name}: {size}x{size}")


def main():
    # iOSのapple-touch-iconは角丸をOS側が付けるため角丸なし
    make_icon(180, APP / "icon-180.png", rounded=False)
    make_icon(192, APP / "icon-192.png", rounded=True)
    make_icon(512, APP / "icon-512.png", rounded=True)


if __name__ == "__main__":
    main()
