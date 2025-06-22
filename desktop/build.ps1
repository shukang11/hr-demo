# HR-Demo Desktop Application Build Script (PowerShell)
# Encoding: UTF-8

param(
    [switch]$Clean = $false,
    [switch]$SkipFrontend = $false,
    [switch]$SkipBackend = $false,
    [switch]$Verbose = $false
)

# Set error handling
$ErrorActionPreference = "Stop"

# Color output functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "[SUCCESS] $Message" "Green"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "[ERROR] $Message" "Red"
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "[INFO] $Message" "Cyan"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "[WARNING] $Message" "Yellow"
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "[STEP] $Message" "Blue"
}

try {
    Write-Step "Starting HR-Demo Desktop Application Build"
    
    # Project paths
    $PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
    $DESKTOP_DIR = Join-Path $PROJECT_ROOT "desktop"
    $API_DIR = Join-Path $PROJECT_ROOT "api"
    $WEB_DIR = Join-Path $PROJECT_ROOT "web"
    
    if ($Verbose) {
        Write-Info "Project root directory: $PROJECT_ROOT"
        Write-Info "Desktop app directory: $DESKTOP_DIR"
        Write-Info "API directory: $API_DIR"
        Write-Info "Web directory: $WEB_DIR"
    }
    
    # Check if directories exist
    if (-not (Test-Path $API_DIR)) {
        Write-Error "API directory does not exist: $API_DIR"
        exit 1
    }
    
    if (-not (Test-Path $WEB_DIR)) {
        Write-Error "Web directory does not exist: $WEB_DIR"
        exit 1
    }
    
    # 1. Check dependencies
    Write-Step "Checking dependencies..."
    
    # Check Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Success "Python installed: $pythonVersion"
    }
    catch {
        Write-Error "Python is not installed or not in PATH"
        exit 1
    }
    
    # Check Bun
    try {
        $bunVersion = bun --version 2>&1
        Write-Success "Bun installed: $bunVersion"
    }
    catch {
        Write-Error "Bun is not installed or not in PATH"
        exit 1
    }
    
    # Check uv
    try {
        $uvVersion = uv --version 2>&1
        Write-Success "uv installed: $uvVersion"
    }
    catch {
        Write-Error "uv is not installed or not in PATH"
        exit 1
    }
    
    Write-Success "Dependencies check completed"    
    # 2. Build frontend
    if (-not $SkipFrontend) {
        Write-Step "Building frontend application..."
        Set-Location $WEB_DIR
        
        Write-Info "Installing frontend dependencies..."
        $bunInstallResult = bun install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Frontend dependency installation failed"
            exit 1
        }
        
        Write-Info "Building frontend application..."
        $bunBuildResult = bun run build:desktop
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Frontend build failed"
            exit 1
        }
        
        Write-Success "Frontend build completed"
    } else {
        Write-Warning "Skipping frontend build"
    }
    
    # 3. Install backend dependencies
    if (-not $SkipBackend) {
        Write-Step "Installing backend dependencies..."
        Set-Location $API_DIR
        
        $uvSyncResult = uv sync --group desktop
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Backend dependency installation failed"
            exit 1
        }
        
        Write-Success "Backend dependencies installed"
    } else {
        Write-Warning "Skipping backend dependency installation"
    }
    
    # 4. Run PyInstaller
    Write-Step "Starting application packaging..."
    Set-Location $DESKTOP_DIR
    
    # Clean previous builds
    if ($Clean) {
        Write-Info "Cleaning previous build files..."
        if (Test-Path "build") {
            Remove-Item -Recurse -Force "build"
            Write-Info "Removed build directory"
        }
        if (Test-Path "dist") {
            Remove-Item -Recurse -Force "dist"
            Write-Info "Removed dist directory"
        }
    }
    
    # Check if spec file exists
    $specFile = "hr_desktop.spec"
    if (-not (Test-Path $specFile)) {
        Write-Error "PyInstaller spec file not found: $specFile"
        Write-Info "Please ensure $specFile exists in $DESKTOP_DIR directory"
        exit 1
    }    # Use PyInstaller to package via uv
    Write-Info "Using PyInstaller to package application..."
    
    # Prepare PyInstaller arguments with proper path
    $specFilePath = Join-Path $DESKTOP_DIR $specFile
    $pyinstallerArgs = @(
        "run",
        "--project", $API_DIR,
        "pyinstaller",
        $specFilePath,
        "--clean",
        "--noconfirm"
    )
    
    if ($Verbose) {
        $pyinstallerArgs += "--log-level=DEBUG"
    }
    
    Write-Info "Running: uv $($pyinstallerArgs -join ' ')"
    $pyinstallerResult = & uv $pyinstallerArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Application packaging failed"
        exit 1
    }
      Write-Success "Application packaging completed"
    
    # 5. Check output (PyInstaller outputs to api/dist, not desktop/dist)
    $OUTPUT_DIR = Join-Path $API_DIR "dist"
    $EXE_DIR = Join-Path $OUTPUT_DIR "HR-Desktop"
    $EXE_FILE = Join-Path $EXE_DIR "HR-Desktop.exe"
    
    if (Test-Path $EXE_FILE) {
        $fileSize = (Get-Item $EXE_FILE).Length
        $fileSizeMB = [math]::Round($fileSize / 1MB, 2)
        
        Write-Success "Success! Application packaged to: $EXE_FILE"
        Write-Info "File size: $fileSizeMB MB"
        Write-Info "Double-click the executable file to launch the application"
        
        # Ask if user wants to run immediately
        $runNow = Read-Host "Do you want to run the application now? (y/N)"
        if ($runNow -eq "y" -or $runNow -eq "Y") {
            Write-Info "Launching application..."
            Start-Process $EXE_FILE
        }
    } else {
        Write-Error "Packaging failed: Executable file not found"
        Write-Info "Expected location: $EXE_FILE"
        Write-Info "Please check PyInstaller output logs"
        exit 1
    }
    
    Write-Step "Build completed successfully!"
    
} catch {
    Write-Error "Error occurred during build process: $($_.Exception.Message)"
    Write-Info "Error details: $($_.Exception.ToString())"
    exit 1
} finally {
    # Return to original directory
    Set-Location $PSScriptRoot
}
