@echo off
chcp 65001 >nul
REM Web UI 의존성 설치 스크립트

echo ========================================
echo Web UI 의존성 설치 중...
echo ========================================
echo.

REM web_ui 폴더에서 프로젝트 루트로 이동
cd /d "%~dp0"
cd ..

echo [1/2] 프론트엔드 의존성 설치 중...
if exist "web_ui\node_modules" (
    echo node_modules 폴더가 이미 존재합니다. 건너뜁니다.
) else (
    cd web_ui
    call npm install
    if errorlevel 1 (
        echo 오류: npm install 실패
        pause
        exit /b 1
    )
    echo 프론트엔드 의존성 설치 완료!
    cd ..
)

echo.
echo [2/2] 백엔드 의존성 설치 중...

REM PyTorch 설치 확인
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo PyTorch가 설치되어 있지 않습니다!
    echo ========================================
    echo.
    echo PyTorch를 설치해야 합니다. 다음 중 하나를 선택하세요:
    echo.
    echo [1] GPU 사용 (CUDA 12.1):
    echo     pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
    echo.
    echo [2] CPU만 사용:
    echo     pip install torch==2.4.0 torchvision==0.19.0
    echo.
    echo 자동으로 CPU 버전을 설치하시겠습니까? (Y/N)
    set /p INSTALL_TORCH="> "
    if /i "%INSTALL_TORCH%"=="Y" (
        echo PyTorch CPU 버전 설치 중...
        pip install torch==2.4.0 torchvision==0.19.0
        if errorlevel 1 (
            echo 오류: PyTorch 설치 실패
            echo 수동으로 설치하세요: pip install torch==2.4.0 torchvision==0.19.0
            pause
            exit /b 1
        )
    ) else (
        echo PyTorch를 수동으로 설치한 후 다시 실행하세요.
        pause
        exit /b 1
    )
) else (
    echo PyTorch가 이미 설치되어 있습니다.
)

REM 나머지 백엔드 의존성 설치
echo 나머지 백엔드 의존성 설치 중...
pip install -r web_ui\src\backend\requirements.txt
if errorlevel 1 (
    echo 오류: 백엔드 의존성 설치 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo 모든 의존성 설치가 완료되었습니다!
echo ========================================
echo.
echo 이제 run_all.bat 또는 run_web_ui.bat을 실행하세요.
echo.
pause
