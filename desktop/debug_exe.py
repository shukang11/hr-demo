"""
调试桌面应用启动问题的脚本
"""

import sys
import traceback
from pathlib import Path


def debug_imports():
    """调试导入问题"""
    print("=== 调试导入问题 ===")
    print(f"Python version: {sys.version}")
    print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
    print(f"sys.executable: {sys.executable}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"__file__ path: {__file__ if '__file__' in globals() else 'N/A'}")

    # 检查sys.path
    print("\nsys.path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")

    try:
        print("\n=== 尝试导入config ===")
        from config import DesktopConfig

        print("✓ 成功导入 DesktopConfig")
        print(f"BASE_DIR: {DesktopConfig.BASE_DIR}")
        print(f"WORK_DIR: {DesktopConfig.WORK_DIR}")
        print(f"API_DIR: {DesktopConfig.API_DIR}")
        print(f"DATABASE_PATH: {DesktopConfig.DATABASE_PATH}")

        # 确保目录存在
        DesktopConfig.ensure_directories()
        print("✓ 目录创建成功")

    except Exception as e:
        print(f"✗ 导入config失败: {e}")
        traceback.print_exc()
        return False

    try:
        print("\n=== 尝试导入 Flask app ===")
        # 添加API路径
        if getattr(sys, "frozen", False):
            api_path = DesktopConfig.API_DIR
        else:
            api_path = Path(__file__).parent.parent / "api"

        if str(api_path) not in sys.path:
            sys.path.insert(0, str(api_path))
            print(f"添加API路径到sys.path: {api_path}")

        from app import create_app

        print("✓ 成功导入 create_app")

        app = create_app(desktop_mode=True)
        print("✓ 成功创建 Flask app")

    except Exception as e:
        print(f"✗ 导入或创建Flask app失败: {e}")
        traceback.print_exc()
        return False

    try:
        print("\n=== 尝试导入 webview ===")
        import webview

        print("✓ 成功导入 webview")

    except Exception as e:
        print(f"✗ 导入webview失败: {e}")
        traceback.print_exc()
        return False

    print("\n=== 所有导入检查完成 ===")
    return True


if __name__ == "__main__":
    try:
        if debug_imports():
            print("\n✓ 所有基础组件导入成功，可能是运行时问题")
        else:
            print("\n✗ 存在导入问题")
    except Exception as e:
        print(f"调试脚本本身出错: {e}")
        traceback.print_exc()

    input("\n按回车键退出...")
