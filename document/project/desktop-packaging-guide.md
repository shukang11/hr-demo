# HR-Demo 桌面应用打包指南

## 概述

本指南介绍如何使用 PyWebView 将 HR-Demo 项目打包成可独立运行的桌面应用程序。该方案将保持现有的前后端分离架构，通过 PyWebView 将 React 前端和 Flask 后端集成为单一的桌面应用。

## 技术方案

### 架构概述
```
┌─────────────────────────────────────┐
│           桌面应用容器               │
│  ┌─────────────────────────────────┐ │
│  │        PyWebView               │ │
│  │  ┌─────────────┐ ┌───────────┐ │ │
│  │  │   React     │ │   Flask   │ │ │
│  │  │   前端      │ │   后端    │ │ │
│  │  │             │ │           │ │ │
│  │  └─────────────┘ └───────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 核心组件
- **PyWebView**: 提供原生窗口容器，嵌入 Web 应用
- **Flask 后端**: 作为本地服务器运行，提供 API 服务
- **React 前端**: 预构建的静态文件，通过 Flask 提供服务
- **PyInstaller**: 将整个应用打包成可执行文件

## 实施步骤

### 阶段1：环境准备和依赖安装

#### 1.1 创建桌面应用目录结构
```
hr-demo/
├── desktop/                  # 新增：桌面应用目录
│   ├── main.py              # 应用启动入口
│   ├── config.py            # 桌面应用配置
│   ├── requirements.txt     # 桌面应用依赖
│   ├── build/               # 构建输出目录
│   └── assets/              # 应用图标等资源
├── api/                     # 现有后端代码
├── web/                     # 现有前端代码
└── document/                # 现有文档
```

#### 1.2 安装 PyWebView 和打包工具
在 `api/pyproject.toml` 中添加桌面应用相关依赖：
```toml
[dependency-groups]
desktop = [
    "pywebview>=4.4.1",
    "pyinstaller>=6.3.0",
    "waitress>=2.1.2"
]
```

### 阶段2：前端构建配置

#### 2.1 修改前端构建配置
修改 `web/vite.config.js`，为桌面应用添加构建选项：
```javascript
export default defineConfig({
  // ...existing config...
  build: {
    outDir: '../desktop/static',  // 输出到桌面应用目录
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: undefined  // 减少文件分片，简化部署
      }
    }
  },
  base: './'  // 使用相对路径，适配本地文件服务
})
```

#### 2.2 构建前端静态文件
```bash
cd web
bun run build
```

### 阶段3：后端适配

#### 3.1 创建桌面应用启动器
创建 `desktop/main.py`：
```python
import webview
import threading
import sys
import os
from pathlib import Path
from waitress import serve
import logging

# 添加 API 路径到 Python 路径
api_path = Path(__file__).parent.parent / "api"
sys.path.insert(0, str(api_path))

from app import create_app

class DesktopApp:
    def __init__(self):
        self.flask_app = None
        self.server_thread = None
        self._setup_logging()
    
    def _setup_logging(self):
        """配置桌面应用日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def start_flask_server(self):
        """在后台线程启动 Flask 服务器"""
        try:
            self.flask_app = create_app()
            # 配置静态文件路径
            static_folder = Path(__file__).parent / "static"
            self.flask_app.static_folder = str(static_folder)
            
            # 使用 waitress 作为 WSGI 服务器
            serve(self.flask_app, host='127.0.0.1', port=5000, threads=4)
        except Exception as e:
            logging.error(f"Flask 服务器启动失败: {e}")
            sys.exit(1)
    
    def create_window(self):
        """创建 PyWebView 窗口"""
        # 等待服务器启动
        import time
        time.sleep(2)
        
        window = webview.create_window(
            title='HR管理系统',
            url='http://127.0.0.1:5000',
            width=1200,
            height=800,
            min_size=(800, 600),
            resizable=True,
            shadow=True,
            on_top=False
        )
        return window
    
    def run(self):
        """启动桌面应用"""
        # 在后台线程启动 Flask 服务器
        self.server_thread = threading.Thread(
            target=self.start_flask_server,
            daemon=True
        )
        self.server_thread.start()
        
        # 创建并启动 PyWebView 窗口
        window = self.create_window()
        webview.start(debug=False)

if __name__ == '__main__':
    app = DesktopApp()
    app.run()
```

#### 3.2 创建配置文件
创建 `desktop/config.py`：
```python
import os
from pathlib import Path

class DesktopConfig:
    """桌面应用配置"""
    
    # 应用基础信息
    APP_NAME = "HR管理系统"
    APP_VERSION = "1.0.0"
    
    # 服务器配置
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 5000
    
    # 窗口配置
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    
    # 路径配置
    BASE_DIR = Path(__file__).parent
    STATIC_DIR = BASE_DIR / "static"
    API_DIR = BASE_DIR.parent / "api"
    
    # 数据库配置（桌面版使用本地SQLite）
    DATABASE_PATH = BASE_DIR / "data" / "hr_desktop.db"
    
    @classmethod
    def ensure_directories(cls):
        """确保必要的目录存在"""
        cls.STATIC_DIR.mkdir(exist_ok=True)
        cls.DATABASE_PATH.parent.mkdir(exist_ok=True)
```

### 阶段4：Flask 应用适配

#### 4.1 修改 Flask 应用以支持桌面模式
在 `api/app.py` 中添加桌面模式支持：
```python
def create_app(config_name='development', desktop_mode=False):
    app = Flask(__name__)
    
    if desktop_mode:
        # 桌面模式特殊配置
        from desktop.config import DesktopConfig
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DesktopConfig.DATABASE_PATH}'
        app.static_folder = str(DesktopConfig.STATIC_DIR)
        
        # 添加根路径路由，服务前端应用
        @app.route('/')
        def serve_frontend():
            return app.send_static_file('index.html')
        
        @app.route('/<path:path>')
        def serve_static_files(path):
            try:
                return app.send_static_file(path)
            except:
                # 对于 SPA 路由，返回 index.html
                return app.send_static_file('index.html')
    
    # ...existing app setup...
    
    return app
```

### 阶段5：打包配置

#### 5.1 创建 PyInstaller 配置
创建 `desktop/build.spec`：
```python
# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# 获取项目路径
project_root = Path(__file__).parent.parent
api_path = project_root / "api"
desktop_path = project_root / "desktop"

a = Analysis(
    ['main.py'],
    pathex=[str(desktop_path), str(api_path)],
    binaries=[],
    datas=[
        (str(desktop_path / 'static'), 'static'),
        (str(api_path / 'instance'), 'instance'),
        (str(api_path / 'migrations'), 'migrations'),
    ],
    hiddenimports=[
        'waitress',
        'webview',
        'flask',
        'sqlalchemy',
        'pydantic',
        'email_validator',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HR管理系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico'  # 应用图标
)

# macOS 应用包配置
if os.name == 'darwin':
    app = BUNDLE(
        exe,
        name='HR管理系统.app',
        icon='assets/app.icns',
        bundle_identifier='com.company.hr-demo',
        info_plist={
            'NSHighResolutionCapable': 'True',
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True
            }
        }
    )
```

#### 5.2 创建构建脚本
创建 `desktop/build.py`：
```python
#!/usr/bin/env python3
"""
桌面应用构建脚本
"""

import subprocess
import sys
import shutil
from pathlib import Path
import logging

class AppBuilder:
    def __init__(self):
        self.desktop_dir = Path(__file__).parent
        self.project_root = self.desktop_dir.parent
        self.web_dir = self.project_root / "web"
        self.api_dir = self.project_root / "api"
        self.build_dir = self.desktop_dir / "build"
        
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def clean_build_dir(self):
        """清理构建目录"""
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(exist_ok=True)
        logging.info("构建目录已清理")
    
    def build_frontend(self):
        """构建前端"""
        logging.info("开始构建前端...")
        try:
            subprocess.run(
                ["bun", "run", "build"],
                cwd=self.web_dir,
                check=True
            )
            logging.info("前端构建完成")
        except subprocess.CalledProcessError as e:
            logging.error(f"前端构建失败: {e}")
            sys.exit(1)
    
    def install_desktop_deps(self):
        """安装桌面应用依赖"""
        logging.info("安装桌面应用依赖...")
        try:
            subprocess.run(
                ["uv", "sync", "--group", "desktop"],
                cwd=self.api_dir,
                check=True
            )
            logging.info("依赖安装完成")
        except subprocess.CalledProcessError as e:
            logging.error(f"依赖安装失败: {e}")
            sys.exit(1)
    
    def run_pyinstaller(self):
        """运行 PyInstaller"""
        logging.info("开始打包应用...")
        try:
            subprocess.run([
                "pyinstaller",
                "--distpath", str(self.build_dir),
                "--workpath", str(self.build_dir / "work"),
                "build.spec"
            ], cwd=self.desktop_dir, check=True)
            logging.info("应用打包完成")
        except subprocess.CalledProcessError as e:
            logging.error(f"应用打包失败: {e}")
            sys.exit(1)
    
    def build(self):
        """执行完整构建流程"""
        self.setup_logging()
        
        logging.info("开始构建 HR-Demo 桌面应用")
        
        # 1. 清理构建目录
        self.clean_build_dir()
        
        # 2. 构建前端
        self.build_frontend()
        
        # 3. 安装依赖
        self.install_desktop_deps()
        
        # 4. 打包应用
        self.run_pyinstaller()
        
        logging.info("构建完成！")
        logging.info(f"应用位置: {self.build_dir}")

if __name__ == "__main__":
    builder = AppBuilder()
    builder.build()
```

### 阶段6：测试和优化

#### 6.1 本地测试
```bash
# 进入桌面应用目录
cd desktop

# 安装依赖
cd ../api && uv sync --group desktop

# 构建前端
cd ../web && bun run build

# 运行桌面应用
cd ../desktop && python main.py
```

#### 6.2 性能优化建议

1. **减少应用体积**：
   - 使用 `--exclude-module` 排除不必要的模块
   - 优化前端构建，移除开发依赖
   - 使用 UPX 压缩可执行文件

2. **提升启动速度**：
   - 预编译 Python 模块
   - 优化数据库连接
   - 使用启动画面遮盖加载时间

3. **增强用户体验**：
   - 添加应用图标和启动画面
   - 实现自动更新机制
   - 添加错误报告功能

## 跨平台注意事项

### Windows
- 需要 Microsoft Visual C++ Redistributable
- 可能需要代码签名证书
- 考虑使用 NSIS 创建安装程序

### macOS
- 需要处理应用签名和公证
- 创建 `.dmg` 安装包
- 处理 Gatekeeper 安全检查

### Linux
- 创建 `.deb` 或 `.rpm` 包
- 处理不同发行版的依赖差异
- 考虑使用 AppImage 格式

## 部署清单

构建完成后，您将获得：
- 可执行文件（Windows: `.exe`, macOS: `.app`, Linux: 二进制文件）
- 所有必要的依赖库
- 静态资源文件
- 数据库文件

## 下一步操作

1. **确认方案**：请确认这个技术方案是否符合您的需求
2. **创建目录结构**：创建 `desktop/` 目录和基础文件
3. **修改配置文件**：更新项目配置以支持桌面模式
4. **测试运行**：验证桌面应用是否正常工作
5. **构建打包**：使用 PyInstaller 创建最终的可执行文件

---

## 风险评估

### 高风险项
- 跨平台兼容性问题
- 打包后的应用体积较大
- 首次启动可能较慢

### 中风险项
- 依赖库版本冲突
- 前后端通信调试复杂
- 不同操作系统的特殊配置

### 缓解措施
- 充分测试各平台
- 优化打包配置
- 准备详细的故障排除指南

---

*此文档将根据实施过程中的发现持续更新*
