# PyInstaller hook for Flask app
# This ensures all Flask templates and static files are included

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集Flask应用的所有数据文件
datas = collect_data_files("flask")

# 收集所有子模块
hiddenimports = collect_submodules("flask")
