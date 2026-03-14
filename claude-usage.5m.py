#!/usr/bin/env python3
# <xbar.title>Claude Usage Monitor</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>はる</xbar.author>
# <xbar.desc>Displays Claude AI usage limits in the menu bar (5h window & weekly)</xbar.desc>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideDisablePlugin>true</swiftbar.hideDisablePlugin>

import subprocess
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ─── Configuration ───────────────────────────────────────────
KEYCHAIN_SERVICE = "Claude Code-credentials"
API_URL = "https://api.anthropic.com/api/oauth/usage"
USER_AGENT = "claude-code/2.0.31"

# Thresholds for color coding (%)
THRESHOLD_WARN = 60
THRESHOLD_DANGER = 85

# ─── Helpers ─────────────────────────────────────────────────

def get_color(utilization: float) -> str:
    """Return hex color based on utilization level."""
    if utilization >= THRESHOLD_DANGER:
        return "#FF4444"   # Red
    elif utilization >= THRESHOLD_WARN:
        return "#FFB020"   # Orange/Yellow
    else:
        return "#44CC44"   # Green


def make_bar(utilization: float, width: int = 15) -> str:
    """Create a simple text progress bar."""
    filled = round(utilization / 100 * width)
    empty = width - filled
    return "█" * filled + "░" * empty


def format_reset_time(reset_str: str | None) -> str:
    """Format ISO reset time to human-readable relative time."""
    if not reset_str:
        return "—"
    try:
        reset_dt = datetime.fromisoformat(reset_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = reset_dt - now
        total_minutes = int(diff.total_seconds() / 60)
        if total_minutes <= 0:
            return "まもなくリセット"
        hours, minutes = divmod(total_minutes, 60)
        if hours > 24:
            days = hours // 24
            hours = hours % 24
            return f"{days}日{hours}時間後"
        elif hours > 0:
            return f"{hours}時間{minutes}分後"
        else:
            return f"{minutes}分後"
    except Exception:
        return "不明"


def get_token() -> str | None:
    """Retrieve Claude Code OAuth token from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-w"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return None
        creds = json.loads(result.stdout.strip())
        return creds.get("claudeAiOauth", {}).get("accessToken")
    except Exception:
        return None


def fetch_usage(token: str) -> dict | None:
    """Fetch usage data from Anthropic API.
    
    Returns:
        dict with usage data on success,
        dict with {"_rate_limited": True, "_retry_after": seconds} on 429,
        None on other errors.
    """
    req = urllib.request.Request(API_URL, headers={
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {token}",
        "anthropic-beta": "oauth-2025-04-20",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 429:
            retry_after = int(e.headers.get("retry-after", 0))
            return {"_rate_limited": True, "_retry_after": retry_after}
        return None
    except Exception:
        return None


# ─── Main ────────────────────────────────────────────────────

def main():
    token = get_token()
    if not token:
        # Menu bar line
        print("☁️ —% | color=#888888")
        print("---")
        print("⚠️ Claude Code の認証情報が見つかりません | color=#FF4444")
        print("Claude Code でログイン後に再試行してください | color=#888888")
        return

    data = fetch_usage(token)
    if not data:
        print("☁️ ⚠ | color=#FF4444")
        print("---")
        print("⚠️ API接続エラー | color=#FF4444")
        print("ネットワーク接続を確認してください | color=#888888")
        return

    # Handle 429 rate limited
    if data.get("_rate_limited"):
        retry_after = data.get("_retry_after", 0)
        hours, minutes = divmod(retry_after // 60, 60)
        if hours > 0:
            reset_str = f"{hours}時間{minutes}分後"
        else:
            reset_str = f"{minutes}分後"
        print(f"🔴 制限中 | color=#FF4444 size=13")
        print("---")
        print(f"⚠️ レート制限に達しています | color=#FF4444 size=13")
        print(f"  リセット: {reset_str} | size=12 color=#888888")
        print("---")
        print("使用状況ページを開く | href=https://claude.ai/settings/usage")
        print("🔄 更新 | refresh=true")
        return

    # Parse usage data
    five_hour = data.get("five_hour") or {}
    seven_day = data.get("seven_day") or {}
    seven_day_opus = data.get("seven_day_opus") or {}

    h5_util = five_hour.get("utilization", 0)
    w_util = seven_day.get("utilization", 0)
    opus_util = seven_day_opus.get("utilization", 0)

    h5_reset = five_hour.get("resets_at")
    w_reset = seven_day.get("resets_at")

    # Determine the "worst" utilization for menu bar display
    max_util = max(h5_util, w_util)
    bar_color = get_color(max_util)

    # ─── Menu Bar Line ───
    # Show the higher of 5h/weekly with an icon
    if max_util >= THRESHOLD_DANGER:
        icon = "🔴"
    elif max_util >= THRESHOLD_WARN:
        icon = "🟡"
    else:
        icon = "🟢"

    print(f"{icon} {h5_util:.0f}% | color={bar_color} size=13")

    # ─── Dropdown ───
    print("---")
    print(f"Claude 使用状況 | size=14 color=#FFFFFF")
    print("---")

    # 5-hour window
    h5_color = get_color(h5_util)
    print(f"⏱ 5時間枠: {h5_util:.1f}% | color={h5_color} size=13")
    print(f"  {make_bar(h5_util)}  {h5_util:.1f}% / 100% | font=Menlo size=12 color={h5_color}")
    print(f"  リセット: {format_reset_time(h5_reset)} | size=11 color=#888888")
    print("---")

    # Weekly
    w_color = get_color(w_util)
    print(f"📅 週間: {w_util:.1f}% | color={w_color} size=13")
    print(f"  {make_bar(w_util)}  {w_util:.1f}% / 100% | font=Menlo size=12 color={w_color}")
    print(f"  リセット: {format_reset_time(w_reset)} | size=11 color=#888888")

    # Opus weekly (show only if > 0)
    if opus_util > 0:
        print("---")
        opus_color = get_color(opus_util)
        print(f"🧠 Opus週間: {opus_util:.1f}% | color={opus_color} size=13")
        print(f"  {make_bar(opus_util)}  {opus_util:.1f}% / 100% | font=Menlo size=12 color={opus_color}")

    print("---")
    print("使用状況ページを開く | href=https://claude.ai/settings/usage")
    print("🔄 更新 | refresh=true")


if __name__ == "__main__":
    main()
