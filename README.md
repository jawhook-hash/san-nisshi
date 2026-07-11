# 餐日誌（さんにっし）

腎臓にやさしい食事の記録帳。CKD（慢性腎臓病）の食事管理のために、
食塩相当量・たんぱく質・エネルギーを記録して見える化する個人用 PWA アプリです。

**アプリ**: https://jawhook-hash.github.io/san-nisshi/

## 機能

- 食品検索（日本食品標準成分表 2,538食品・ひらがな検索対応）
- 外食チェーンのメニュー記録（ジョイフル・コメダ珈琲店・資さんうどん）
- パッケージの栄養成分表示の読み取り（iOSの「テキストをスキャン」＋自動抽出）
- マイメニュー（よく食べる食事のワンタップ記録）
- 今日の残量ゲージ・30日推移グラフ・体重/血圧/eGFR記録・CSV出力
- オフライン動作（Service Worker）。記録データはすべて端末内にのみ保存

## 使い方（iPhone）

1. Safari で上記URLを開く
2. 共有ボタン →「ホーム画面に追加」
3. ホーム画面の「餐日誌」から起動

## データの更新（開発者向け）

```powershell
# 食品DB（文科省の成分表Excelを raw/seibunhyo_honhyo.xlsx に置いてから）
python build_food_db.py

# 外食チェーンDB
python chains/fetch_joyfull.py   # 公式PDFを raw/joyfull_cal.pdf に置いてから
python chains/fetch_komeda.py
python chains/fetch_sukesan.py
python chains/build_chains_db.py

# アプリ更新時は docs/sw.js の CACHE 名も変更すること
```

## データ出典と注意

- 食品成分: 「日本食品標準成分表（八訂）増補2023年」（文部科学省）
- 外食: 各社公式サイト公開情報（コメダはカロリーのみ公開。資さんは公式冷凍商品の表示に基づく参考値）
- 本アプリは記録のための道具であり、医学的判断は行いません。目標値は必ず主治医・管理栄養士に確認してください
