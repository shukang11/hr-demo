#!/usr/bin/env python3
"""
桌面应用完整测试脚本
测试打包后的应用是否正常运行
"""

import sys
import os
import subprocess
import time
import requests
import logging
from pathlib import Path


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def test_app_executable():
    """测试应用可执行文件"""
    logger = setup_logging()

    desktop_dir = Path(__file__).parent
    dist_dir = desktop_dir / "dist"

    # 检查打包结果
    if sys.platform == "darwin":
        app_path = dist_dir / "HR-Desktop.app"
        exe_path = app_path / "Contents/MacOS/HR-Desktop"

        if not app_path.exists():
            logger.error("❌ macOS应用包不存在")
            return False

        if not exe_path.exists():
            logger.error("❌ 应用可执行文件不存在")
            return False

        logger.info("✅ macOS应用包存在")

        # 检查应用包结构
        contents_dir = app_path / "Contents"
        if not contents_dir.exists():
            logger.error("❌ 应用包结构不完整")
            return False

        logger.info("✅ 应用包结构完整")

        # 测试应用启动（后台模式）
        logger.info("🧪 测试应用启动...")
        try:
            # 使用timeout限制测试时间
            process = subprocess.Popen(
                ["timeout", "10", "open", str(app_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 等待几秒
            time.sleep(5)

            # 检查是否有进程在运行
            check_process = subprocess.run(
                ["pgrep", "-f", "HR-Desktop"], capture_output=True, text=True
            )

            if check_process.returncode == 0:
                logger.info("✅ 应用成功启动")

                # 尝试访问本地服务器
                try:
                    response = requests.get("http://127.0.0.1:5000", timeout=3)
                    if response.status_code == 200:
                        logger.info("✅ 本地服务器响应正常")
                        success = True
                    else:
                        logger.warning(f"⚠️ 服务器响应异常: {response.status_code}")
                        success = False
                except requests.RequestException as e:
                    logger.warning(f"⚠️ 无法连接到服务器: {e}")
                    success = False

                # 清理进程
                subprocess.run(["pkill", "-f", "HR-Desktop"], capture_output=True)
                return success
            else:
                logger.error("❌ 应用启动失败")
                return False

        except Exception as e:
            logger.error(f"❌ 测试过程出错: {e}")
            return False

    else:
        exe_path = dist_dir / "HR-Desktop"
        if not exe_path.exists():
            logger.error("❌ 可执行文件不存在")
            return False

        logger.info("✅ 可执行文件存在")
        # 其他平台的测试逻辑...
        return True


def test_file_sizes():
    """测试文件大小"""
    logger = setup_logging()

    desktop_dir = Path(__file__).parent
    dist_dir = desktop_dir / "dist"

    if sys.platform == "darwin":
        app_path = dist_dir / "HR-Desktop.app"
        if app_path.exists():
            # 计算应用包大小
            result = subprocess.run(
                ["du", "-sh", str(app_path)], capture_output=True, text=True
            )

            if result.returncode == 0:
                size = result.stdout.split()[0]
                logger.info(f"📏 应用包大小: {size}")

                # 检查大小是否合理（应该在100M-500M之间）
                if "M" in size:
                    size_num = float(size.replace("M", ""))
                    if 100 <= size_num <= 500:
                        logger.info("✅ 应用包大小合理")
                        return True
                    else:
                        logger.warning(f"⚠️ 应用包大小异常: {size}")
                        return False
                else:
                    logger.warning(f"⚠️ 无法解析应用包大小: {size}")
                    return False
            else:
                logger.error("❌ 无法获取应用包大小")
                return False
        else:
            logger.error("❌ 应用包不存在")
            return False

    return True


def test_static_files():
    """测试静态文件是否正确打包"""
    logger = setup_logging()

    desktop_dir = Path(__file__).parent
    static_dir = desktop_dir / "static"

    if not static_dir.exists():
        logger.error("❌ 静态文件目录不存在")
        return False

    # 检查关键文件
    index_file = static_dir / "index.html"
    if not index_file.exists():
        logger.error("❌ index.html 不存在")
        return False

    assets_dir = static_dir / "assets"
    if not assets_dir.exists():
        logger.error("❌ assets 目录不存在")
        return False

    # 检查assets目录中的文件
    asset_files = list(assets_dir.glob("*"))
    if len(asset_files) == 0:
        logger.error("❌ assets 目录为空")
        return False

    logger.info(f"✅ 静态文件检查通过 ({len(asset_files)} 个资源文件)")
    return True


def main():
    """主测试函数"""
    logger = setup_logging()

    logger.info("🚀 开始桌面应用完整测试")
    logger.info("=" * 50)

    tests = [
        ("静态文件测试", test_static_files),
        ("文件大小测试", test_file_sizes),
        ("应用可执行测试", test_app_executable),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} 执行失败: {e}")
            results.append((test_name, False))

    logger.info("\n" + "=" * 50)
    logger.info("📊 测试结果总结:")

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1

    logger.info(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        logger.info("🎉 所有测试通过！桌面应用打包成功！")
        logger.info(f"🚀 可以使用以下命令启动应用:")
        if sys.platform == "darwin":
            logger.info(f"   open {Path(__file__).parent}/dist/HR-Desktop.app")
        else:
            logger.info(f"   {Path(__file__).parent}/dist/HR-Desktop")
        return 0
    else:
        logger.error("⚠️ 部分测试失败，请检查打包配置。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
