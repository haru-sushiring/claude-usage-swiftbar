# ☁️ Claude Usage Monitor for SwiftBar

macOS メニューバーに Claude の使用量をリアルタイム表示する [SwiftBar](https://github.com/swiftbar/SwiftBar) プラグインです。

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![macOS](https://img.shields.io/badge/macOS-13.0+-black)
![License](https://img.shields.io/badge/license-MIT-green)

## 表示イメージ

| 状態 | メニューバー | 意味 |
|------|-------------|------|
| 余裕あり | 🟢 12% | 安心して使える |
| やや消費 | 🟡 65% | そろそろ意識 |
| 残りわずか | 🔴 90% | セーブしよう |

クリックすると、5時間ローリングウィンドウ・週間キャップ・Opus週間枠のプログレスバーとリセットまでの残り時間が表示されます。

## 必要なもの

- macOS 13.0+
- [SwiftBar](https://github.com/swiftbar/SwiftBar)（または [xbar](https://xbarapp.com/) でも動作可）
- Python 3.10+（macOS 標準で可）
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) でログイン済み（`claude login`）

## セットアップ

### 自動（推奨）

```bash
git clone https://github.com/<your-username>/claude-usage-swiftbar.git
cd claude-usage-swiftbar
chmod +x setup.sh
./setup.sh
```

### 手動

```bash
# 1. SwiftBar をインストール
brew install --cask swiftbar

# 2. プラグインディレクトリを作成
mkdir -p ~/.swiftbar-plugins

# 3. プラグインを配置
cp claude-usage.5m.py ~/.swiftbar-plugins/
chmod +x ~/.swiftbar-plugins/claude-usage.5m.py

# 4. SwiftBar を起動し、プラグインフォルダに ~/.swiftbar-plugins を指定
open -a SwiftBar
```

> **Tip:** フォルダ選択ダイアログでは `Cmd + Shift + G` を押して `~/.swiftbar-plugins` と入力してください。`.` で始まるフォルダは Finder で非表示のため直接入力が必要です。

## 仕組み

1. macOS Keychain から Claude Code の OAuth トークンを取得
2. `https://api.anthropic.com/api/oauth/usage` を呼び出して使用状況を取得
3. メニューバーに使用率を表示（5分ごとに自動更新）

認証情報はスクリプトに含まれません。すべて実行時に Keychain から読み取るため、リポジトリの公開は安全です。

## 更新間隔の変更

ファイル名の `.5m.` の部分が更新間隔を制御しています。

```bash
# 例: 1分間隔にする場合
mv claude-usage.5m.py claude-usage.1m.py

# 例: 15分間隔にする場合
mv claude-usage.5m.py claude-usage.15m.py
```

| ファイル名 | 間隔 |
|-----------|------|
| `claude-usage.1m.py` | 1分 |
| `claude-usage.5m.py` | 5分 |
| `claude-usage.15m.py` | 15分 |
| `claude-usage.1h.py` | 1時間 |

## API レスポンス例

```json
{
  "five_hour": {
    "utilization": 12.0,
    "resets_at": "2026-03-14T10:59:59.943648+00:00"
  },
  "seven_day": {
    "utilization": 35.0,
    "resets_at": "2026-03-17T03:59:59.943679+00:00"
  },
  "seven_day_opus": {
    "utilization": 0.0,
    "resets_at": null
  }
}
```

## トラブルシューティング

| 症状 | 原因と対処 |
|------|-----------|
| `☁️ —%` と表示される | Claude Code でログインしていない → `claude login` を実行 |
| `☁️ ⚠` と表示される | API 接続エラー → ネットワーク接続を確認 |
| メニューバーに何も出ない | SwiftBar が起動していない、またはプラグインフォルダが正しく設定されていない |

## ライセンス

MIT
