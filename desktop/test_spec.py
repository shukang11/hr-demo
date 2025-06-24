import os
import sys
from pathlib import Path

# 测试数据收集
SPECPATH = os.path.dirname(os.path.abspath(__file__))
project_root = Path(SPECPATH).resolve().parent
desktop_static_path = project_root / "desktop" / "static"

print(f"[TEST] SPECPATH: {SPECPATH}")
print(f"[TEST] Project root: {project_root}")
print(f"[TEST] Desktop static path: {desktop_static_path}")
print(f"[TEST] Desktop static exists: {desktop_static_path.exists()}")

if desktop_static_path.exists():
    import glob

    static_files = list(desktop_static_path.rglob("*"))
    print(f"[TEST] Found {len(static_files)} files in static directory")
    for i, file_path in enumerate(static_files[:10]):  # 只显示前10个
        print(f"[TEST] File {i + 1}: {file_path}")
