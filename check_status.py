"""
喝水提醒 - 状态检测工具 🚰
检查程序是否正在运行
"""
import subprocess
import sys


def check_running():
    """通过 tasklist 检查 pythonw.exe 进程"""
    try:
        # 用 /fi 过滤只查 pythonw.exe，速度最快
        result = subprocess.run(
            ['tasklist', '/fi', 'IMAGENAME eq pythonw.exe', '/nh'],
            capture_output=True, text=True, timeout=5,
            encoding='gbk', errors='replace'
        )
        output = result.stdout.strip()

        if 'pythonw.exe' in output:
            # 还在运行，提取 PID
            lines = [l for l in output.split('\n') if 'pythonw.exe' in l]
            if lines:
                parts = lines[0].split()
                pid = parts[1] if len(parts) > 1 else '?'
                mem = parts[-1] if len(parts) > 1 else '?'
                print(f"  PID: {pid}  |  内存: {mem}")
            return True
        return False

    except subprocess.TimeoutExpired:
        print("  检测超时，请稍后重试")
        return None
    except Exception as e:
        print(f"  检测出错: {e}")
        return None


def main():
    print("=" * 45)
    print("  Water Reminder - Status Check")
    print("=" * 45)
    print()

    status = check_running()

    if status is True:
        print("  >>> pythonw.exe is RUNNING <<<")
        print("  ✅ 程序正在运行！")
        print()
        print("  📍 查看方式：")
        print("     1. 任务栏右下角 → 找水滴图标 💧")
        print("     2. 右键水滴图标 → 可设置间隔/暂停/退出")
        print("     3. 任务管理器 → pythonw.exe 进程")
    elif status is False:
        print("  >>> pythonw.exe NOT found <<<")
        print("  ❌ 程序未运行")
        print()
        print("  📍 启动方式：")
        print("     1. 双击 start.bat（弹出窗口后按任意键关闭）")
        print("     2. 或双击 start_silent.vbs（完全无窗口）")
        print("     3. 重启电脑（已设置开机自启）")
    else:
        print("  ❓ 无法确定状态")

    print()
    print("=" * 45)

    if len(sys.argv) < 2 or sys.argv[1] != '--no-pause':
        input("\n按 Enter 退出...")


if __name__ == "__main__":
    main()
