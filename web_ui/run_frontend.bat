@echo off
chcp 65001 >nul
REM Web UI 프론트엔드 실행 스크립트

echo ========================================
echo Web UI 프론트엔드 실행 중...
echo ========================================
echo.

REM web_ui 폴더로 이동
cd /d "%~dp0"

REM 의존성 확인 및 설치
if not exist "node_modules" (
    echo npm 의존성 설치 중...
    call npm install
    if errorlevel 1 (
        echo 오류: npm install 실패
        pause
        exit /b 1
    )
)

echo 프론트엔드 서버 시작 중...
echo http://localhost:3000 에서 실행됩니다.
echo.
call npm run dev

pause
