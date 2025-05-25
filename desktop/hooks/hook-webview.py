# PyInstaller hook for PyWebView
# This ensures all PyWebView dependencies are properly included

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集PyWebView的数据文件
datas = collect_data_files("webview")

# 收集PyWebView的所有子模块
hiddenimports = collect_submodules("webview")

# 添加特定的隐藏导入
hiddenimports += [
    "webview.platforms",
    "webview.platforms.cocoa",
    "webview.platforms.qt",
    "webview.platforms.gtk",
    "webview.platforms.winforms",
]
