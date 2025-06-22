"""
桌面应用配置验证脚本
用于测试不同环境下的路径配置是否正确
"""

import sys
from pathlib import Path

# 添加desktop路径
desktop_path = Path(__file__).parent
sys.path.insert(0, str(desktop_path))

# 必须在路径设置后导入
from config import DesktopConfig  # noqa: E402


def test_config():
    """测试配置是否正确"""
    print("=" * 50)
    print("桌面应用配置验证")
    print("=" * 50)

    # 检测运行环境
    is_frozen = getattr(sys, "frozen", False)
    print(f"运行环境: {'打包环境' if is_frozen else '开发环境'}")
    print(f"Python路径: {sys.executable}")
    print(f"当前脚本: {__file__}")

    print("\n" + "-" * 30)
    print("路径配置信息")
    print("-" * 30)

    # 显示所有路径配置
    paths = {
        "BASE_DIR": DesktopConfig.BASE_DIR,
        "WORK_DIR": getattr(DesktopConfig, "WORK_DIR", "N/A"),
        "STATIC_DIR": DesktopConfig.STATIC_DIR,
        "API_DIR": getattr(DesktopConfig, "API_DIR", "N/A"),
        "DATABASE_PATH": DesktopConfig.DATABASE_PATH,
        "LOGS_DIR": getattr(DesktopConfig, "LOGS_DIR", "N/A"),
        "UPLOADS_DIR": getattr(DesktopConfig, "UPLOADS_DIR", "N/A"),
    }

    for name, path in paths.items():
        if path != "N/A":
            exists = path.exists() if hasattr(path, "exists") else False
            print(f"{name:15}: {path} {'✓' if exists else '✗'}")
        else:
            print(f"{name:15}: 未配置")

    print("\n" + "-" * 30)
    print("目录创建测试")
    print("-" * 30)

    try:
        DesktopConfig.ensure_directories()
        print("✓ 目录创建成功")
        # 再次检查目录是否存在
        for name, path in paths.items():
            if path != "N/A" and hasattr(path, "exists"):
                if name == "DATABASE_PATH":
                    # 数据库路径检查父目录是否存在
                    if path.parent.exists():
                        print(f"✓ {name} 父目录存在")
                    else:
                        print(f"✗ {name} 父目录不存在")
                elif path.exists():
                    print(f"✓ {name} 目录存在")
                else:
                    print(f"✗ {name} 目录不存在")

    except Exception as e:
        print(f"✗ 目录创建失败: {e}")

    print("\n" + "=" * 50)
    print("验证完成")
    print("=" * 50)


if __name__ == "__main__":
    test_config()
