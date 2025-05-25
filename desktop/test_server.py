#!/usr/bin/env python3
"""
桌面应用测试脚本
测试Flask服务器是否能正常启动和服务静态文件
"""

import sys
import time
import threading
from pathlib import Path

# 添加 API 路径到 Python 路径
api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))

from waitress import serve
from app import create_app
from config import DesktopConfig


def test_flask_server():
    """测试Flask服务器"""
    print("正在测试桌面应用Flask服务器...")

    try:
        # 创建Flask应用
        app = create_app(desktop_mode=True)

        # 确保必要的目录存在
        DesktopConfig.ensure_directories()

        print(f"静态文件目录: {app.static_folder}")
        print(f"数据库URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

        # 检查静态文件是否存在
        static_index = Path(app.static_folder) / "index.html"
        if static_index.exists():
            print("✅ 前端静态文件存在")
        else:
            print("❌ 前端静态文件不存在，请先运行: bun run build:desktop")
            return False

        # 在后台线程启动服务器
        def start_server():
            serve(app, host="127.0.0.1", port=5000, threads=4)

        server_thread = threading.Thread(target=start_server, daemon=True)
        server_thread.start()

        # 等待服务器启动
        time.sleep(2)

        # 测试HTTP请求
        import requests

        try:
            # 测试根路径
            response = requests.get("http://127.0.0.1:5000/", timeout=5)
            if response.status_code == 200:
                print("✅ 根路径测试成功")
            else:
                print(f"❌ 根路径测试失败: {response.status_code}")

            # 测试API路径
            response = requests.get("http://127.0.0.1:5000/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ API路径测试成功")
            else:
                print(f"❌ API路径测试失败: {response.status_code}")

            print("✅ Flask服务器测试通过")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP请求测试失败: {e}")
            return False

    except Exception as e:
        print(f"❌ Flask服务器测试失败: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    if test_flask_server():
        print("\n✅ 桌面应用后端测试成功！")
        print("你可以继续测试完整的桌面应用: python main.py")
    else:
        print("\n❌ 桌面应用后端测试失败")
        sys.exit(1)
