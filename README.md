# ビルエネルギーシミュレーションアプリ v2.0

オフィスビルのエネルギー収支と室内環境を月単位で評価するモダンなWebアプリケーション

## 🌟 主な特徴

- **モダンなUI**: React + TypeScript + Tailwind CSSによる美しいインターフェース
- **高速API**: FastAPIによる高性能バックエンド
- **リアルタイムシミュレーション**: 即座に結果を可視化
- **キャリブレーション機能**: 実測データとの比較・自動最適化
- **レスポンシブデザイン**: デスクトップ・タブレット・モバイル対応
- **Docker対応**: 簡単なセットアップと開発環境

## 📚 ドキュメント

- **[利用ガイド](doc/user_guide.md)**: 基本操作とワークフロー例
- **[エネルギー計算理論](doc/energy_calculation.md)**: 計算式とパラメータの詳細説明
- **[キャリブレーション機能ガイド](doc/calibration_guide.md)**: 実測データとの比較・自動調整方法

## 📋 技術スタック

### フロントエンド
- **React 18**: UIライブラリ
- **TypeScript**: 型安全な開発
- **Vite**: 高速ビルドツール
- **Tailwind CSS**: モダンなスタイリング
- **Recharts**: データ可視化
- **Axios**: HTTP クライアント

### バックエンド
- **FastAPI**: 高性能Pythonフレームワーク
- **Pydantic**: データバリデーション
- **Uvicorn**: ASGIサーバー
- **NumPy/Pandas**: 数値計算

## 🚀 クイックスタート

### Docker Composeを使用（推奨）

```bash
# リポジトリのクローン
git clone <repository-url>
cd ccw-hvac_model

# Docker Composeでアプリケーションを起動
docker-compose up -d

# フロントエンド: http://localhost:3000
# バックエンドAPI: http://localhost:8000
# API ドキュメント: http://localhost:8000/docs
```

### ローカル開発環境

#### バックエンドのセットアップ

```bash
cd backend

# 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存パッケージのインストール
pip install -r requirements.txt

# サーバーの起動
uvicorn app.main:app --reload --port 8000
```

#### フロントエンドのセットアップ

```bash
cd frontend

# 依存パッケージのインストール
npm install

# 開発サーバーの起動
npm run dev
```

## 📂 プロジェクト構造

```
ccw-hvac_model/
├── backend/                    # FastAPI バックエンド
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py      # APIエンドポイント
│   │   ├── models/
│   │   │   ├── building_energy_model.py  # コアモデル
│   │   │   └── presets.py     # プリセット設定
│   │   ├── schemas/
│   │   │   └── __init__.py    # Pydantic スキーマ
│   │   └── main.py            # FastAPI アプリケーション
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React フロントエンド
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts      # API クライアント
│   │   ├── components/
│   │   │   ├── PresetSelector.tsx
│   │   │   └── ResultsChart.tsx
│   │   ├── types/
│   │   │   └── index.ts       # TypeScript 型定義
│   │   ├── App.tsx            # メインアプリケーション
│   │   └── main.tsx           # エントリーポイント
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── src/                        # レガシーコード（参照用）
│   ├── building_energy_model.py
│   ├── presets.py
│   ├── sample_run.py
│   └── test_building_energy_model.py
├── doc/
│   ├── QUICKSTART.md
│   └── USER_MANUAL.md
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## 🔌 API エンドポイント

### シミュレーション

- `POST /api/v1/simulate` - シミュレーション実行
- `GET /api/v1/presets` - プリセット一覧取得
- `GET /api/v1/presets/modern` - 最新オフィスプリセット取得
- `GET /api/v1/presets/old` - 旧式オフィスプリセット取得
- `POST /api/v1/config/save` - 設定保存
- `POST /api/v1/results/save` - 結果保存

### キャリブレーション

- `POST /api/v1/compare` - シミュレーション結果と実測データの比較
- `POST /api/v1/calibrate` - パラメータ自動調整

### その他

- `GET /api/v1/health` - ヘルスチェック

詳細なAPI仕様は http://localhost:8000/docs で確認できます。

## 💻 使用方法

### 1. アプリケーションへのアクセス

ブラウザで http://localhost:3000 にアクセス

### 2. 設定タブ

- **プリセット選択**: 最新オフィスまたは旧式オフィスを選択
- **建物仕様**: 床面積、壁・窓のU値などを編集
- **設備仕様**: 照明、空調システムの性能を編集
- **月別条件**: 外気温、室内設定、運転時間などを12ヶ月分編集
- **設定保存/読込**: JSON形式で設定を保存・読込

### 3. シミュレーションタブ

- 「シミュレーション実行」ボタンをクリック
- **結果サマリー**: 年間エネルギー消費量、総負荷、平均負荷を表示
- 「結果保存」でCSV形式でエクスポート可能

### 4. 結果タブ

- **月別エネルギー消費グラフ**: 全館空調、個別空調、照明、OA機器
- **月別負荷グラフ**: 顕熱負荷、潜熱負荷、SHF
- **インタラクティブ**: グラフにマウスオーバーで詳細表示

### 5. キャリブレーションタブ

- **実測データ入力**: 手動入力またはCSVインポート
- **比較実行**: シミュレーション結果と実測データを比較
- **評価メトリックス**: RMSE、MAE、MAPE、R²を表示
- **パラメータ選択**: 調整したいパラメータと範囲を設定
- **キャリブレーション実行**: グリッドサーチまたは統計的最適化
- **結果確認**: 最適化されたパラメータを自動適用、改善度を視覚的に確認

詳細は[利用ガイド](doc/user_guide.md)と[キャリブレーション機能ガイド](doc/calibration_guide.md)を参照してください。

## 🧪 テスト

### バックエンドテスト

```bash
cd backend
python -m pytest

# または既存のテストスクリプト
cd ..
python src/test_building_energy_model.py
```

### フロントエンドビルド

```bash
cd frontend
npm run build
```

## 🔧 開発

### バックエンド開発

- FastAPIは自動的にコード変更を検知してリロードします
- http://localhost:8000/docs でインタラクティブなAPIドキュメントにアクセス

### フロントエンド開発

- Viteの高速HMR（Hot Module Replacement）により、変更が即座に反映されます
- TypeScriptによる型チェックで安全な開発

## 📊 計算モデル

### 入力パラメータ

- **建物仕様**: 床面積、天井高、壁・窓のU値、日射熱取得係数
- **設備仕様**: 照明・OA機器電力密度、空調システム性能（COP等）
- **運用条件**: 外気温湿度、室内設定、居住者数、運転時間（月別）

### 計算内容

- **熱負荷**: 顕熱負荷（壁・窓貫流、日射、内部発熱）、潜熱負荷
- **エネルギー**: 全館空調（外調機、熱源）、個別空調のエネルギー消費量
- **空気線図**: エンタルピー、顕熱比の計算

## 🎨 UI機能

- **ダークモード対応**: システム設定に応じて自動切替
- **レスポンシブデザイン**: モバイル、タブレット、デスクトップ対応
- **インタラクティブグラフ**: Rechartsによる美しいデータ可視化
- **ローディング状態**: シミュレーション実行中の視覚的フィードバック

## 🔐 本番環境デプロイ

### 環境変数設定

```bash
# フロントエンド (.env)
VITE_API_URL=https://your-api-domain.com/api/v1

# バックエンド (環境変数)
CORS_ORIGINS=https://your-frontend-domain.com
```

### ビルドと実行

```bash
# フロントエンド
cd frontend
npm run build
# distフォルダをホスティングサービスにデプロイ

# バックエンド
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📝 ライセンス

このプロジェクトはMITライセンスのもとで公開されています。

## 👥 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📧 お問い合わせ

質問や提案がある場合は、issueを作成してください。

---

**バージョン**: 2.0.0
**最終更新**: 2024年11月
