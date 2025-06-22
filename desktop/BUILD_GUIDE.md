# HR-Demo Desktop Build Scripts Usage Guide

## Overview

This directory contains build scripts for packaging the HR-Demo application as a desktop application.

## Scripts

### PowerShell Script (Recommended for Windows)

**File:** `build.ps1`

#### Basic Usage

```powershell
# Basic build
.\build.ps1

# Build with options
.\build.ps1 -Clean -Verbose

# Skip frontend build (if already built)
.\build.ps1 -SkipFrontend

# Skip backend dependencies (if already installed)
.\build.ps1 -SkipBackend
```

#### Parameters

- `-Clean`: Remove previous build files before building
- `-SkipFrontend`: Skip frontend build process
- `-SkipBackend`: Skip backend dependency installation
- `-Verbose`: Enable detailed logging

#### Prerequisites

1. **Python** - Required for the backend API
2. **Bun** - Required for frontend build
3. **uv** - Required for Python dependency management
4. **PyInstaller** - Will be installed via uv
5. **PyInstaller Spec File** - `hr_desktop.spec` (now included)

#### Build Process

1. **Dependency Check**: Verifies all required tools are installed
2. **Frontend Build**: Builds the React frontend using Bun
3. **Backend Dependencies**: Installs Python dependencies using uv
4. **Application Packaging**: Uses PyInstaller to create executable

#### Output

The packaged application will be created at:
```
desktop/dist/HR-Desktop.exe
```

### Batch Script (Legacy)

**File:** `build.bat`

Basic batch script for Windows systems. Use PowerShell script for better functionality.

## Troubleshooting

### Common Issues

1. **Encoding Issues**: PowerShell script uses English text to avoid encoding problems
2. **Missing Dependencies**: The script will check and report missing tools
3. **Build Failures**: Check the console output for specific error messages

### Error Solutions

- **Python not found**: Install Python and add to PATH
- **Bun not found**: Install Bun from https://bun.sh/
- **uv not found**: Install uv from https://docs.astral.sh/uv/
- **Spec file missing**: Ensure `hr_desktop.spec` exists in the desktop directory

## Development

### Quick Development Build

For development, you can skip time-consuming steps:

```powershell
# Skip frontend if no changes made
.\build.ps1 -SkipFrontend

# Skip backend deps if already installed
.\build.ps1 -SkipBackend

# Clean build with verbose output
.\build.ps1 -Clean -Verbose
```

### Manual Steps

If you prefer manual control:

1. Build frontend:
   ```bash
   cd ../web
   bun install
   bun run build:desktop
   ```

2. Install backend dependencies:
   ```bash
   cd ../api
   uv sync --group desktop
   ```

3. Package application:
   ```bash
   cd .
   pyinstaller hr_desktop.spec --clean --noconfirm
   ```

## Notes

- The script automatically switches between directories as needed
- All paths are resolved relative to the project root
- The script includes error handling and will exit on failures
- Build artifacts are placed in the `dist/` directory
