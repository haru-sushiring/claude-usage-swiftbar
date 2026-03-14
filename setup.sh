#!/bin/bash
# Claude Usage Monitor - セットアップスクリプト
# macOS メニューバーに Claude 使用量を表示する

set -e

echo "☁️  Claude Usage Monitor セットアップ"
echo "======================================"
echo ""

# ─── 1. SwiftBar のインストール確認 ───
if ! brew list --cask swiftbar &>/dev/null 2>&1; then
    echo "📦 SwiftBar をインストールします..."
    brew install --cask swiftbar
    echo "✅ SwiftBar インストール完了"
else
    echo "✅ SwiftBar は既にインストール済み"
fi

# ─── 2. プラグインディレクトリの設定 ───
PLUGIN_DIR="$HOME/.swiftbar-plugins"
mkdir -p "$PLUGIN_DIR"
echo "📂 プラグインディレクトリ: $PLUGIN_DIR"

# ─── 3. プラグインの配置 ───
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_SRC="$SCRIPT_DIR/claude-usage.5m.py"
PLUGIN_DST="$PLUGIN_DIR/claude-usage.5m.py"

if [ ! -f "$PLUGIN_SRC" ]; then
    echo "❌ claude-usage.5m.py が見つかりません"
    echo "   このスクリプトと同じディレクトリに配置してください"
    exit 1
fi

cp "$PLUGIN_SRC" "$PLUGIN_DST"
chmod +x "$PLUGIN_DST"
echo "✅ プラグインを配置しました"

# ─── 4. Claude Code 認証確認 ───
echo ""
echo "🔑 Claude Code の認証情報を確認中..."
if security find-generic-password -s "Claude Code-credentials" -w &>/dev/null 2>&1; then
    echo "✅ 認証情報が見つかりました"
else
    echo "⚠️  認証情報が見つかりません"
    echo "   Claude Code でログイン済みであることを確認してください:"
    echo "   $ claude login"
fi

# ─── 5. 完了 ───
echo ""
echo "======================================"
echo "✅ セットアップ完了！"
echo ""
echo "📋 次のステップ:"
echo "  1. SwiftBar を起動（初回はプラグインフォルダを聞かれます）"
echo "     → 「$PLUGIN_DIR」を指定してください"
echo "  2. メニューバーに 🟢 XX% が表示されれば成功です"
echo ""
echo "⚙️  設定:"
echo "  - 更新間隔: 5分ごと（ファイル名の .5m. で制御）"
echo "  - 変更したい場合はファイル名を変更:"
echo "    .1m. = 1分  .5m. = 5分  .15m. = 15分  .1h. = 1時間"
echo ""
echo "SwiftBar を起動しますか？ (y/N)"
read -r answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    open -a SwiftBar
    echo "🚀 SwiftBar を起動しました"
fi
