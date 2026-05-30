"""
一键设置喝水提醒开机自启动 🚰
"""
import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STARTUP_DIR = os.path.join(
    os.environ["APPDATA"],
    r"Microsoft\Windows\Start Menu\Programs\Startup",
)
PYTHONW_PATH = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
VBS_PATH = os.path.join(SCRIPT_DIR, "start_silent.vbs")
SHORTCUT_PATH = os.path.join(STARTUP_DIR, "喝水提醒.lnk")

# ── 1. 创建 VBS 静默启动脚本 ────────────────────────────────────
vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "{PYTHONW_PATH}" & chr(34) & " " & chr(34) & "{SCRIPT_DIR}\\water_reminder.py" & chr(34), 0, False
'''

with open(VBS_PATH, "w", encoding="utf-8") as f:
    f.write(vbs_content)

print(f"✅ 已创建静默启动脚本: {VBS_PATH}")

# ── 2. 创建快捷方式到 Startup 文件夹 ────────────────────────────
ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{SHORTCUT_PATH}")
$Shortcut.TargetPath = "{VBS_PATH}"
$Shortcut.WorkingDirectory = "{SCRIPT_DIR}"
$Shortcut.Description = "喝水提醒小助手 - 每30分钟提醒喝水"
$Shortcut.Save()
'''

result = subprocess.run(
    ["powershell", "-NoProfile", "-Command", ps_script],
    capture_output=True,
    text=True,
)

if result.returncode == 0:
    print(f"✅ 已添加快捷方式到开机启动文件夹")
    print(f"📍 位置: {SHORTCUT_PATH}")
else:
    print(f"❌ 创建快捷方式失败: {result.stderr}")
    sys.exit(1)

# ── 3. 验证 ─────────────────────────────────────────────────────
if os.path.exists(SHORTCUT_PATH):
    print(f"\n🎉 开机自启动设置成功！")
    print("\n下次开机时，喝水提醒将自动运行在系统托盘。")
    print("如果想立即启动，可以双击 start.bat")
else:
    print("\n⚠️  快捷方式似乎没有创建成功，请手动检查。")

input("\n按 Enter 键退出...")
