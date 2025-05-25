#!/usr/bin/env python3
"""
开发环境测试脚本
用于在打包前测试桌面应用的各个组件
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
api_path = project_root / "api"
sys.path.insert(0, str(api_path))


def test_flask_server():
    """测试Flask服务器"""
    print("🧪 测试Flask服务器...")

    try:
        from app import create_app

        app = create_app(desktop_mode=True)

        # 测试应用创建
        print("✅ Flask应用创建成功")

        # 测试配置
        print(f"✅ 数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        print(f"✅ 静态文件夹: {app.static_folder}")

        return True
    except Exception as e:
        print(f"❌ Flask服务器测试失败: {e}")
        return False


def test_dependencies():
    """测试依赖是否正确安装"""
    print("🧪 测试依赖...")

    dependencies = [
        "flask",
        "webview",
        "waitress",
        "sqlalchemy",
        "flask_sqlalchemy",
        "flask_migrate",
    ]

    failed = []

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep}")
            failed.append(dep)

    if failed:
        print(f"❌ 缺少依赖: {', '.join(failed)}")
        return False

    print("✅ 所有依赖测试通过")
    return True


def test_static_files():
    """测试静态文件"""
    print("🧪 测试静态文件...")

    static_dir = Path(__file__).parent / "static"

    if not static_dir.exists():
        print("❌ 静态文件目录不存在")
        return False

    index_file = static_dir / "index.html"
    if not index_file.exists():
        print("❌ index.html 不存在")
        return False

    assets_dir = static_dir / "assets"
    if not assets_dir.exists():
        print("❌ assets 目录不存在")
        return False

    print("✅ 静态文件测试通过")
    return True


def test_database():
    """测试数据库连接"""
    print("🧪 测试数据库...")

    try:
        from config import DesktopConfig

        DesktopConfig.ensure_directories()

        if DesktopConfig.DATABASE_PATH.exists():
            print("✅ 数据库文件存在")
        else:
            print("⚠️  数据库文件不存在，但这是正常的（首次运行时会创建）")

        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False


def run_full_test():
    """运行完整的应用测试"""
    print("🧪 启动完整应用测试...")

    # 在后台启动桌面应用
    desktop_script = Path(__file__).parent / "main.py"

    try:
        # 启动应用（不显示窗口，仅测试服务器）
        env = os.environ.copy()
        env["WEBVIEW_HIDDEN"] = "1"  # 隐藏窗口用于测试

        process = subprocess.Popen(
            [sys.executable, str(desktop_script)],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # 等待服务器启动
        time.sleep(3)

        # 测试HTTP响应
        try:
            response = requests.get("http://127.0.0.1:5000", timeout=5)
            if response.status_code == 200:
                print("✅ 服务器响应正常")
                success = True
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                success = False
        except requests.RequestException as e:
            print(f"❌ 无法连接到服务器: {e}")
            success = False

        # 停止进程
        process.terminate()
        process.wait(timeout=5)

        return success

    except Exception as e:
        print(f"❌ 完整测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 开始桌面应用测试")
    print("=" * 50)

    tests = [
        ("依赖测试", test_dependencies),
        ("静态文件测试", test_static_files),
        ("数据库测试", test_database),
        ("Flask服务器测试", test_flask_server),
        # ("完整应用测试", run_full_test),  # 暂时注释掉，避免窗口弹出
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 执行失败: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("📊 测试结果总结:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！可以进行打包。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
