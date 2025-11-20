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
set "WEB_UI_DIR=%ROOT_DIR%\web_ui"
echo 프로젝트 루트: %ROOT_DIR%
echo Web UI 디렉토리: %WEB_UI_DIR%

REM web_ui 폴더 존재 확인
if not exist "%WEB_UI_DIR%" (
    echo 오류: web_ui 폴더를 찾을 수 없습니다.
    echo 현재 위치: %ROOT_DIR%
    pause
    exit /b 1
)

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

REM npm이 설치되어 있는지 확인
where npm >nul 2>&1
if errorlevel 1 (
    echo 오류: npm을 찾을 수 없습니다. Node.js가 설치되어 있는지 확인하세요.
    echo Node.js 다운로드: https://nodejs.org/
    pause
    exit /b 1
)

REM node_modules 확인 및 설치
if not exist "%WEB_UI_DIR%\node_modules" (
    echo npm 의존성 설치 중...
    cd "%WEB_UI_DIR%"
    call npm install
    if errorlevel 1 (
        echo 오류: npm install 실패
        pause
        exit /b 1
    )
    cd "%ROOT_DIR%"
)

REM 백엔드 의존성 확인
if not exist "%WEB_UI_DIR%\src\backend\__pycache__" (
    echo 백엔드 의존성 확인 중...
    cd "%WEB_UI_DIR%\src\backend"
    pip install -r requirements.txt >nul 2>&1
    cd "%ROOT_DIR%"
)

REM 백엔드 실행 (새 창)
echo 백엔드 서버 시작 중...
start "Web UI Backend - Port 5000" cmd /k "chcp 65001 >nul && cd /d %WEB_UI_DIR%\src\backend && title Web UI Backend Server - Port 5000 && echo ======================================== && echo 백엔드 서버 시작 중... && echo 포트: 5000 && echo ======================================== && echo. && where conda >nul 2>&1 && if not errorlevel 1 (call conda.bat activate pytorch-img2img) && python app.py && echo. && echo 백엔드 서버가 종료되었습니다. && pause"
if errorlevel 1 (
    echo 오류: 백엔드 서버 시작 실패
    pause
    exit /b 1
)
timeout /t 3 /nobreak >nul

REM 프론트엔드 실행 (새 창)
echo 프론트엔드 서버 시작 중...
start "Web UI Frontend - Port 5173" cmd /k "chcp 65001 >nul && cd /d %WEB_UI_DIR% && title Web UI Frontend Server - Port 5173 && echo ======================================== && echo 프론트엔드 서버 시작 중... && echo 포트: 5173 && echo ======================================== && echo. && npx vite && echo. && echo 프론트엔드 서버가 종료되었습니다. && pause"
if errorlevel 1 (
    echo 오류: 프론트엔드 서버 시작 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo 두 서버가 실행되었습니다!
echo ========================================
echo 프론트엔드: http://localhost:5173
echo 백엔드: http://localhost:5000
echo.
echo 서버를 종료하려면 각 창을 닫으세요.
echo.
echo 3초 후 브라우저가 자동으로 열립니다...
echo.
echo 참고: 포트 5173이 사용 중이면 Vite가 다른 포트(5174, 5175 등)를 사용할 수 있습니다.
echo 터미널 창에서 실제 포트 번호를 확인하세요.
timeout /t 5 /nobreak >nul
REM 프론트엔드 포트는 동적으로 변경될 수 있으므로 여러 포트 시도
start http://localhost:5173 2>nul
timeout /t 1 /nobreak >nul
start http://localhost:5174 2>nul
echo.
echo 프론트엔드 서버 터미널 창에서 표시된 주소로 접속하세요.
echo 일반적으로: http://localhost:5173 또는 http://localhost:5174
echo.
pause

