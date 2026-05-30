"""
喝水提醒小助手 🚰
==================
系统托盘常驻程序，每间隔一段时间弹窗提醒你喝水。
"""

import sys
import threading
import time
import os
import json
from datetime import datetime

# ── 依赖检查与导入 ─────────────────────────────────────────────
try:
    from plyer import notification
except ImportError:
    print("正在安装依赖 plyer...")
    os.system(f"{sys.executable} -m pip install plyer -q")
    from plyer import notification

try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("正在安装依赖 pystray / Pillow...")
    os.system(f"{sys.executable} -m pip install pystray pillow -q")
    import pystray
    from PIL import Image, ImageDraw, ImageFont

# ── 配置 ────────────────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULT_CONFIG = {
    "interval_minutes": 30,  # 提醒间隔（分钟）
    "enabled": True,         # 是否启用
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            # 合并默认值，确保新字段存在
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            return dict(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


config = load_config()
reminder_active = config["enabled"]
interval_minutes = config["interval_minutes"]

# ── 图标生成 ─────────────────────────────────────────────────────
ICON_SIZE = 64


def create_icon(size=ICON_SIZE, active=True):
    """绘制一个水滴/水杯图标"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    r = size // 2 - 4

    if active:
        # 蓝色水滴
        color_fill = (30, 144, 255, 255)      # 道奇蓝
        color_outline = (20, 120, 220, 255)
    else:
        # 灰色水滴
        color_fill = (160, 160, 160, 255)
        color_outline = (120, 120, 120, 255)

    # 画水滴形状：椭圆底部 + 尖顶
    # 用圆 + 三角形组合近似
    draw.ellipse(
        [cx - r // 2, cy - r // 4, cx + r // 2, cy + r // 2],
        fill=color_fill,
        outline=color_outline,
        width=2,
    )
    # 水滴顶部
    draw.polygon(
        [
            (cx, cy - r // 2 - 2),
            (cx - r // 3, cy - r // 6),
            (cx + r // 3, cy - r // 6),
        ],
        fill=color_fill,
        outline=color_outline,
        width=2,
    )

    # 高光
    draw.ellipse(
        [cx - r // 6, cy - r // 8, cx - r // 12, cy + r // 8],
        fill=(255, 255, 255, 100),
    )

    return img


# ── 提醒逻辑 ────────────────────────────────────────────────────
def send_notification():
    """发送 Windows 系统通知"""
    now = datetime.now().strftime("%H:%M")
    try:
        notification.notify(
            title="💧 喝水时间到！",
            message=(
                f"已经 {interval_minutes} 分钟没喝水啦！\n"
                f"起来活动一下，接杯水喝一口吧 ☕\n"
                f"当前时间：{now}"
            ),
            app_name="WaterReminder",
            timeout=10,
        )
    except Exception as e:
        print(f"通知发送失败: {e}")


def reminder_loop(stop_event):
    """后台循环定时提醒"""
    while not stop_event.is_set():
        if reminder_active:
            send_notification()
        # 等待指定的间隔（秒）
        stop_event.wait(interval_minutes * 60)
        if stop_event.is_set():
            break


stop_event = threading.Event()
reminder_thread = None


def start_reminder():
    global reminder_thread, stop_event
    if reminder_thread is not None and reminder_thread.is_alive():
        return  # 已经在运行
    stop_event.clear()
    reminder_thread = threading.Thread(target=reminder_loop, args=(stop_event,), daemon=True)
    reminder_thread.start()


def stop_reminder():
    global stop_event
    stop_event.set()


# ── 托盘菜单回调 ─────────────────────────────────────────────────
def on_enable_toggle(icon, item):
    global reminder_active
    reminder_active = not reminder_active
    config["enabled"] = reminder_active
    save_config(config)
    if reminder_active:
        # 重新启动循环
        stop_reminder()
        start_reminder()
    else:
        stop_reminder()
    icon.icon = create_icon(active=reminder_active)
    icon.update_menu()


def on_drink_now(icon, item):
    """立即提醒一次"""
    send_notification()


def on_set_interval(icon, item):
    """弹出菜单选择间隔"""
    # 用 pystray 的子菜单实现，在菜单创建时动态生成
    pass


def on_set_interval_30(icon, item):
    global interval_minutes
    interval_minutes = 30
    config["interval_minutes"] = 30
    save_config(config)
    restart_reminder()
    icon.update_menu()


def on_set_interval_45(icon, item):
    global interval_minutes
    interval_minutes = 45
    config["interval_minutes"] = 45
    save_config(config)
    restart_reminder()
    icon.update_menu()


def on_set_interval_60(icon, item):
    global interval_minutes
    interval_minutes = 60
    config["interval_minutes"] = 60
    save_config(config)
    restart_reminder()
    icon.update_menu()


def on_set_interval_120(icon, item):
    global interval_minutes
    interval_minutes = 120
    config["interval_minutes"] = 120
    save_config(config)
    restart_reminder()
    icon.update_menu()


def restart_reminder():
    stop_reminder()
    if reminder_active:
        start_reminder()


def on_quit(icon, item):
    stop_reminder()
    icon.stop()


def get_enable_text(item=None):
    return "✅ 已启用" if reminder_active else "❌ 已暂停"


# ── 检查标记函数（显示当前选中间隔） ────────────────────────────
def checked_30(item=None):
    return interval_minutes == 30


def checked_45(item=None):
    return interval_minutes == 45


def checked_60(item=None):
    return interval_minutes == 60


def checked_120(item=None):
    return interval_minutes == 120


# ── 主函数 ───────────────────────────────────────────────────────
def main():
    icon = pystray.Icon(
        "water-reminder",
        create_icon(active=reminder_active),
        menu=pystray.Menu(
            pystray.MenuItem(
                get_enable_text,
                on_enable_toggle,
                default=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "💧 立即提醒一次",
                on_drink_now,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "⏱ 提醒间隔",
                pystray.Menu(
                    pystray.MenuItem("30 分钟", on_set_interval_30, checked=checked_30, radio=True),
                    pystray.MenuItem("45 分钟", on_set_interval_45, checked=checked_45, radio=True),
                    pystray.MenuItem("60 分钟", on_set_interval_60, checked=checked_60, radio=True),
                    pystray.MenuItem("120 分钟", on_set_interval_120, checked=checked_120, radio=True),
                ),
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("🚪 退出", on_quit),
        ),
    )

    icon.run()


if __name__ == "__main__":
    # 先启动提醒线程再进入托盘循环
    if reminder_active:
        start_reminder()
    main()
