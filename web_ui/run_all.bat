@echo off
REM Web UI Integration Script (Frontend + Backend)

setlocal enabledelayedexpansion

REM Set code page to UTF-8
chcp 65001 >nul 2>&1

REM Verify batch file is running
echo ========================================
echo Starting Web UI...
echo ========================================
echo.
echo Script path: %~dp0
echo Current directory: %CD%
echo.
echo Continuing in 3 seconds...
timeout /t 3 /nobreak >nul
echo.

REM Move from web_ui folder to project root
echo [1] Moving to script location...
cd /d "%~dp0" 2>nul
if not exist "%~dp0" (
    echo ERROR: Cannot find script path: %~dp0
    echo.
    pause
    exit /b 1
)
echo   Current location: %CD%

REM Move to parent directory (project root)
echo [2] Moving to project root...
cd .. 2>nul
if errorlevel 1 (
    echo ERROR: Failed to move to parent directory
    echo Current location: %CD%
    echo.
    pause
    exit /b 1
)
echo   Current location: %CD%

set "ROOT_DIR=%CD%"
echo [3] Project root: %ROOT_DIR%

REM Activate conda environment
echo [4] Activating conda environment...
REM Check if conda is available
where conda >nul 2>&1
if errorlevel 1 (
    echo WARNING: conda not found in PATH. Trying to use conda from common locations...
    REM Try to find conda in common locations
    if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
        set "CONDA_BASE=%USERPROFILE%\anaconda3"
        set "PATH=%CONDA_BASE%\Scripts;%CONDA_BASE%\Library\bin;%PATH%"
    ) else if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
        set "CONDA_BASE=%USERPROFILE%\miniconda3"
        set "PATH=%CONDA_BASE%\Scripts;%CONDA_BASE%\Library\bin;%PATH%"
    ) else if exist "C:\ProgramData\anaconda3\Scripts\conda.exe" (
        set "CONDA_BASE=C:\ProgramData\anaconda3"
        set "PATH=%CONDA_BASE%\Scripts;%CONDA_BASE%\Library\bin;%PATH%"
    ) else (
        echo WARNING: conda not found. Running without conda environment.
        goto :skip_conda
    )
)

REM Initialize conda for batch file
call conda.bat activate pytorch-img2img 2>nul
if errorlevel 1 (
    echo WARNING: Failed to activate conda environment 'pytorch-img2img'
    echo Trying alternative method...
    REM Try alternative activation method
    if exist "%CONDA_BASE%\Scripts\activate.bat" (
        call "%CONDA_BASE%\Scripts\activate.bat" pytorch-img2img
    ) else (
        echo WARNING: Could not activate conda environment. Running without it.
        goto :skip_conda
    )
)

REM Verify conda environment is activated
if not "%CONDA_DEFAULT_ENV%"=="pytorch-img2img" (
    echo WARNING: Conda environment may not be activated correctly.
    echo Current environment: %CONDA_DEFAULT_ENV%
    echo Continuing anyway...
) else (
    echo   Conda environment activated: %CONDA_DEFAULT_ENV%
)

:skip_conda

REM Check if web_ui folder exists
echo [5] Checking web_ui folder...
if not exist "%ROOT_DIR%\web_ui" (
    echo ERROR: web_ui folder not found.
    echo Current location: %ROOT_DIR%
    echo Looking for: %ROOT_DIR%\web_ui
    echo.
    echo Directory listing:
    dir /b /ad
    echo.
    pause
    exit /b 1
)
echo   web_ui folder found

REM Create temporary batch file for backend
echo [6] Creating backend temporary file...
set "TEMP_BACKEND=%TEMP%\web_ui_backend_%RANDOM%.bat"
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT_DIR%"
    echo REM Activate conda environment
    echo where conda ^>nul 2^>^&1
    echo if not errorlevel 1 ^(
    echo     call conda.bat activate pytorch-img2img
    echo ^)
    echo python web_ui\src\backend\app.py
    echo pause
) > "%TEMP_BACKEND%" 2>nul

if not exist "%TEMP_BACKEND%" (
    echo ERROR: Failed to create backend temporary file
    echo Temp directory: %TEMP%
    echo.
    pause
    exit /b 1
)
echo   Backend temp file created: %TEMP_BACKEND%

REM Create temporary batch file for frontend
echo [7] Creating frontend temporary file...
set "TEMP_FRONTEND=%TEMP%\web_ui_frontend_%RANDOM%.bat"
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT_DIR%\web_ui"
    echo npm run dev
    echo pause
) > "%TEMP_FRONTEND%" 2>nul

if not exist "%TEMP_FRONTEND%" (
    echo ERROR: Failed to create frontend temporary file
    echo Temp directory: %TEMP%
    del "%TEMP_BACKEND%" 2>nul
    echo.
    pause
    exit /b 1
)
echo   Frontend temp file created: %TEMP_FRONTEND%

REM Start backend (new window)
echo [8] Starting backend server...
start "Web UI Backend" cmd /k ""%TEMP_BACKEND%""
if errorlevel 1 (
    echo ERROR: Failed to start backend server
    del "%TEMP_BACKEND%" 2>nul
    del "%TEMP_FRONTEND%" 2>nul
    echo.
    pause
    exit /b 1
)
echo   Backend server window opened.
timeout /t 2 /nobreak >nul

REM Start frontend (new window)
echo [9] Starting frontend server...

REM Check if npm is installed
where npm >nul 2>&1
if errorlevel 1 (
    echo WARNING: npm not found. Please check if Node.js is installed.
    echo Running backend only.
    goto :end
)

if not exist "%ROOT_DIR%\web_ui\node_modules" (
    echo   Installing npm dependencies...
    cd "%ROOT_DIR%\web_ui"
    if errorlevel 1 (
        echo ERROR: Failed to move to web_ui folder
        del "%TEMP_BACKEND%" 2>nul
        del "%TEMP_FRONTEND%" 2>nul
        echo.
        pause
        exit /b 1
    )
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed
        del "%TEMP_BACKEND%" 2>nul
        del "%TEMP_FRONTEND%" 2>nul
        echo.
        pause
        exit /b 1
    )
    cd "%ROOT_DIR%"
)

start "Web UI Frontend" cmd /k ""%TEMP_FRONTEND%""
if errorlevel 1 (
    echo ERROR: Failed to start frontend server
    del "%TEMP_BACKEND%" 2>nul
    del "%TEMP_FRONTEND%" 2>nul
    echo.
    pause
    exit /b 1
)
echo   Frontend server window opened.

:end

echo.
echo ========================================
echo Servers started successfully!
echo ========================================
echo Frontend: http://localhost:3000
echo Backend: http://localhost:5000
echo.
echo Close each window to stop the servers.
echo You can close this window.
echo.
timeout /t 3 /nobreak >nul
