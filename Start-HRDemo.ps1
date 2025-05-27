# Start-HRDemo.ps1 - HR-Demo Launcher for Windows

<#
.SYNOPSIS
    Launches the HR-Demo application.
    This script sets up a Python virtual environment using a provided embedded Python distribution,
    ensures pip is installed in the virtual environment (bootstrapping if necessary),
    installs dependencies from a requirements file, and then runs the main application.

.DESCRIPTION
    The script performs the following steps:
    1. Verifies the provided embedded Python distribution.
    2. Creates a Python virtual environment (.venv) if it doesn't exist, using the embedded distribution.
    3. Checks for pip in the virtual environment; if missing, uses the provided get-pip.py to install it.
    4. Installs or updates application dependencies from 'api/desktop-requirements.txt' using pip.
    5. Checks for the presence of pre-built frontend assets in 'web-dist/'.
    6. Starts the HR-Demo desktop application (desktop/main.py).

.NOTES
    Author: GitHub Copilot
    Version: 1.2.0
    Target OS: Windows 11
    Python Version: 3.11.9 (embeddable package provided by user)

    Prerequisites:
    - A Python 3.11.9 embeddable distribution must be present in 'PythonDist/python-embed/' relative to this script.
    - 'get-pip.py' must be present in 'PythonDist/' relative to this script.
    - 'api/desktop-requirements.txt' must exist and contain the Python package dependencies.
    - Frontend assets should be pre-built and located in the 'web-dist' folder.
    - PowerShell execution policy might need to be adjusted (e.g., Set-ExecutionPolicy RemoteSigned -Scope CurrentUser).
#>

# --- Configuration Section ---
$ProjectName = "HR-Demo"
$PythonVersionRequired = "3.11.9" # For verification

# Paths are relative to the script's location ($PSScriptRoot)
$PythonDistBaseDir = Join-Path $PSScriptRoot "PythonDist"
$EmbeddedPythonSubDir = "python-embed" # Updated path
$PythonDistDir = Join-Path $PythonDistBaseDir $EmbeddedPythonSubDir

$VenvDir = Join-Path $PSScriptRoot ".venv"
$RequirementsFile = Join-Path $PSScriptRoot "api" "desktop-requirements.txt"
$MainScriptPath = Join-Path $PSScriptRoot "desktop" "main.py"
$WebDistPath = Join-Path $PSScriptRoot "web-dist"
$LogFile = Join-Path $PSScriptRoot "hr-demo-launcher.log"

$GetPipScriptPath = Join-Path $PythonDistBaseDir "get-pip.py" # Updated path for get-pip.py

# --- Helper Functions ---
function Write-Log {
    param (
        [string]$Message,
        [string]$Level = "INFO" # INFO, WARNING, ERROR
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Host $LogEntry
    Add-Content -Path $LogFile -Value $LogEntry
}

# --- Main Logic ---
Clear-Content -Path $LogFile -ErrorAction SilentlyContinue # Clear log file on new run
Write-Log "Initializing $ProjectName Launcher (v1.2.0)..."
Write-Log "Script Location: $PSScriptRoot"
Write-Log "Expected Embedded Python Directory: $PythonDistDir"
Write-Log "Virtual Environment Directory: $VenvDir"
Write-Log "Requirements File: $RequirementsFile"
Write-Log "Main Application Script: $MainScriptPath"
Write-Log "Frontend Assets Directory: $WebDistPath"

# 1. Verify Python Distribution
Write-Log "Step 1: Verifying Embedded Python Distribution..."
$EmbeddedPythonExe = Join-Path $PythonDistDir "python.exe"

if (-not (Test-Path $EmbeddedPythonExe -PathType Leaf)) {
    Write-Log "FATAL: Embedded python.exe not found at '$EmbeddedPythonExe'." -Level ERROR
    Write-Log "Please ensure the Python $PythonVersionRequired embeddable distribution is correctly placed in '$PythonDistDir'." -Level ERROR
    Read-Host "Press Enter to exit."
    exit 1
}
Write-Log "Using Python interpreter from embedded distribution: $EmbeddedPythonExe"

# Check Python version from the distribution
try {
    $VersionOutput = & $EmbeddedPythonExe --version 2>&1
    Write-Log "Provided Python version: $VersionOutput"
    if ($VersionOutput -notmatch $PythonVersionRequired.Replace(".","\\.")) {
         Write-Log "WARNING: Provided Python version ('$VersionOutput') does not exactly match expected '$PythonVersionRequired'. Proceeding, but ensure compatibility." -Level WARNING
    }
} catch {
    Write-Log "WARNING: Could not determine Python version from '$EmbeddedPythonExe'. Error: $($_.Exception.Message)" -Level WARNING
}

# 2. Create/Verify Virtual Environment
Write-Log "Step 2: Setting up Python Virtual Environment..."
$VenvPythonExe = Join-Path $VenvDir "Scripts" "python.exe"
$VenvPipExe = Join-Path $VenvDir "Scripts" "pip.exe"

if (-not (Test-Path $VenvDir -PathType Container)) {
    Write-Log "Virtual environment not found at '$VenvDir'. Creating using '$EmbeddedPythonExe'..."
    try {
        & $EmbeddedPythonExe -m venv $VenvDir
        Write-Log "Virtual environment created successfully at '$VenvDir'."
    } catch {
        Write-Log "FATAL: Failed to create virtual environment. Error: $($_.Exception.Message)" -Level ERROR
        Write-Log "Ensure the embedded Python's '_pth' file (e.g., python${PythonVersionRequired.Replace('.','') }._pth) is configured correctly if issues persist (e.g., 'import site' uncommented)." -Level ERROR
        Read-Host "Press Enter to exit."
        exit 1
    }
} else {
    Write-Log "Virtual environment found at '$VenvDir'."
    if (-not (Test-Path $VenvPythonExe -PathType Leaf)) {
        Write-Log "WARNING: Virtual environment at '$VenvDir' seems incomplete (missing Scripts\\python.exe). Consider deleting the .venv folder and re-running the script." -Level WARNING
    }
}

# 3. Ensure pip is installed in the Virtual Environment
Write-Log "Step 3: Ensuring pip is installed in the virtual environment..."
if (-not (Test-Path $VenvPipExe -PathType Leaf)) {
    Write-Log "'pip.exe' not found in virtual environment ('$VenvPipExe'). Attempting to bootstrap pip using '$GetPipScriptPath'..."
    
    if (-not (Test-Path $GetPipScriptPath -PathType Leaf)) {
        Write-Log "FATAL: get-pip.py script not found at '$GetPipScriptPath'." -Level ERROR
        Write-Log "Please ensure 'get-pip.py' is placed in the '$PythonDistBaseDir' directory." -Level ERROR
        Read-Host "Press Enter to exit."
        exit 1
    }
    Write-Log "Found get-pip.py at '$GetPipScriptPath'."

    # Run get-pip.py using the virtual environment's Python
    Write-Log "Running get-pip.py using '$VenvPythonExe'..."
    try {
        & $VenvPythonExe $GetPipScriptPath
        Write-Log "pip bootstrapping process completed."
        # Verify pip is now installed
        if (-not (Test-Path $VenvPipExe -PathType Leaf)) {
            Write-Log "FATAL: pip installation via get-pip.py failed. 'pip.exe' still not found in '$VenvPipExe'." -Level ERROR
            Read-Host "Press Enter to exit."
            exit 1
        }
        Write-Log "pip successfully installed in the virtual environment."
    } catch {
        Write-Log "FATAL: Failed to execute get-pip.py. Error: $($_.Exception.Message)" -Level ERROR
        Read-Host "Press Enter to exit."
        exit 1
    }
    # No longer need to clean up get-pip.py as it's part of the distribution package
} else {
    Write-Log "pip.exe already exists in the virtual environment: '$VenvPipExe'."
}

# 4. Install/Update Dependencies
Write-Log "Step 4: Installing/Updating dependencies..."
if (-not (Test-Path $RequirementsFile -PathType Leaf)) {
    Write-Log "FATAL: Requirements file not found at '$RequirementsFile'." -Level ERROR
    Read-Host "Press Enter to exit."
    exit 1
}

Write-Log "Installing dependencies from '$RequirementsFile' using '$VenvPipExe'..."
try {
    # Use pip from the virtual environment
    & $VenvPipExe install -r $RequirementsFile --no-cache-dir --disable-pip-version-check
    Write-Log "Dependencies installed/updated successfully."
} catch {
    Write-Log "FATAL: Failed to install dependencies. Error: $($_.Exception.Message)" -Level ERROR
    # Attempt to get more detailed pip error if possible (this can be complex)
    # For now, the raw exception message should give some clues.
    Read-Host "Press Enter to exit."
    exit 1
}

# 5. Check Frontend Assets
Write-Log "Step 5: Checking for frontend assets..."
if (-not (Test-Path $WebDistPath -PathType Container) -or -not (Test-Path (Join-Path $WebDistPath "index.html") -PathType Leaf)) {
    Write-Log "WARNING: Frontend assets directory '$WebDistPath' or 'index.html' within it was not found." -Level WARNING
    Write-Log "The application might not display correctly. Ensure frontend assets are pre-built and placed in '$WebDistPath'." -Level WARNING
    # Depending on strictness, this could be a fatal error.
} else {
    Write-Log "Frontend assets check passed (found '$WebDistPath\index.html')."
}

# 6. Launch Application
Write-Log "Step 6: Launching $ProjectName application..."
if (-not (Test-Path $MainScriptPath -PathType Leaf)) {
    Write-Log "FATAL: Main application script not found at '$MainScriptPath'." -Level ERROR
    Read-Host "Press Enter to exit."
    exit 1
}

Write-Log "Executing: $VenvPythonExe $MainScriptPath"
try {
    # Start the application. Use Start-Process if you want it in a new window and want the script to potentially continue.
    # For a console app that this script "becomes", direct execution is fine.
    & $VenvPythonExe $MainScriptPath
    Write-Log "$ProjectName has finished."
} catch {
    Write-Log "FATAL: Failed to launch $ProjectName. Error: $($_.Exception.Message)" -Level ERROR
    Read-Host "Press Enter to exit."
    exit 1
}

Write-Log "Launcher script finished."
# Optional: Add a final Read-Host if the app closes immediately and you want to see logs.
# Read-Host "Application has closed. Press Enter to exit this launcher."
