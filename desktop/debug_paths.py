import sys
import os
print(f"sys.executable: {sys.executable}")
print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
print(f"sys._MEIPASS: {getattr(sys, '_MEIPASS', 'Not found')}")
print(f"__file__: {__file__}")
print(f"Current working directory: {os.getcwd()}")
print(f"Executable directory: {os.path.dirname(sys.executable)}")

# 模拟路径检测逻辑
from pathlib import Path
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    desktop_path = Path(sys.executable).parent
    print(f"PyInstaller mode - desktop_path: {desktop_path}")
else:
    desktop_path = Path(__file__).parent.parent / "desktop"
    print(f"Development mode - desktop_path: {desktop_path}")

print(f"Desktop path exists: {desktop_path.exists()}")
print(f"Desktop path contents: {list(desktop_path.iterdir()) if desktop_path.exists() else 'Directory does not exist'}")
