@echo off
chcp 65001 >nul
REM Web UI 통합 실행 스크립트 (프론트엔드 + 백엔드)

echo ========================================
echo Web UI 실행 중...
echo ========================================
echo.

REM 현재 스크립트 위치에서 프로젝트 루트로 이동
cd /d "%~dp0"
if errorlevel 1 (
    echo 오류: 스크립트 위치로 이동 실패
    pause
    exit /b 1
)
set "ROOT_DIR=%CD%"
echo 현재 디렉토리: %ROOT_DIR%

REM Activate conda environment
echo Activating conda environment...
where conda >nul 2>&1
if not errorlevel 1 (
    call conda.bat activate pytorch-img2img 2>nul
    if errorlevel 1 (
        echo WARNING: Failed to activate conda environment 'pytorch-img2img'
        echo Trying alternative method...
        if exist "%USERPROFILE%\anaconda3\Scripts\activate.bat" (
            call "%USERPROFILE%\anaconda3\Scripts\activate.bat" pytorch-img2img
        ) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
            call "%USERPROFILE%\miniconda3\Scripts\activate.bat" pytorch-img2img
        )
    )
    if "%CONDA_DEFAULT_ENV%"=="pytorch-img2img" (
        echo Conda environment activated: %CONDA_DEFAULT_ENV%
    )
)

REM web_ui 폴더 존재 확인
if not exist "%ROOT_DIR%\web_ui" (
    echo 오류: web_ui 폴더를 찾을 수 없습니다.
    echo 현재 위치: %ROOT_DIR%
    pause
    exit /b 1
)

REM 임시 배치 파일 생성 (백엔드)
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
) > "%TEMP_BACKEND%"

if errorlevel 1 (
    echo 오류: 백엔드 임시 파일 생성 실패
    pause
    exit /b 1
)

REM 임시 배치 파일 생성 (프론트엔드)
set "TEMP_FRONTEND=%TEMP%\web_ui_frontend_%RANDOM%.bat"
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo cd /d "%ROOT_DIR%\web_ui"
    echo npm run dev
    echo pause
) > "%TEMP_FRONTEND%"

if errorlevel 1 (
    echo 오류: 프론트엔드 임시 파일 생성 실패
    del "%TEMP_BACKEND%" 2>nul
    pause
    exit /b 1
)

REM 백엔드 실행 (새 창)
echo 백엔드 서버 시작 중...
start "Web UI Backend" cmd /k ""%TEMP_BACKEND%""
if errorlevel 1 (
    echo 오류: 백엔드 서버 시작 실패
    del "%TEMP_BACKEND%" 2>nul
    del "%TEMP_FRONTEND%" 2>nul
    pause
    exit /b 1
)
timeout /t 2 /nobreak >nul

REM 프론트엔드 실행 (새 창)
echo 프론트엔드 서버 시작 중...
if not exist "%ROOT_DIR%\web_ui\node_modules" (
    echo npm 의존성 설치 중...
    cd "%ROOT_DIR%\web_ui"
    if errorlevel 1 (
        echo 오류: web_ui 폴더로 이동 실패
        del "%TEMP_BACKEND%" 2>nul
        del "%TEMP_FRONTEND%" 2>nul
        pause
        exit /b 1
    )
    call npm install
    if errorlevel 1 (
        echo 오류: npm install 실패
        del "%TEMP_BACKEND%" 2>nul
        del "%TEMP_FRONTEND%" 2>nul
        pause
        exit /b 1
    )
    cd "%ROOT_DIR%"
)

REM npm이 설치되어 있는지 확인
where npm >nul 2>&1
if errorlevel 1 (
    echo 경고: npm을 찾을 수 없습니다. Node.js가 설치되어 있는지 확인하세요.
    echo 백엔드만 실행합니다.
) else (
    start "Web UI Frontend" cmd /k ""%TEMP_FRONTEND%""
    if errorlevel 1 (
        echo 오류: 프론트엔드 서버 시작 실패
        del "%TEMP_BACKEND%" 2>nul
        del "%TEMP_FRONTEND%" 2>nul
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 두 서버가 실행되었습니다!
echo ========================================
echo 프론트엔드: http://localhost:3000
echo 백엔드: http://localhost:5000
echo.
echo 서버를 종료하려면 각 창을 닫으세요.
echo.
pause
