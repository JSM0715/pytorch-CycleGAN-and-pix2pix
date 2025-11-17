@echo off
chcp 65001 >nul
REM Web UI 백엔드 실행 스크립트

echo ========================================
echo Web UI 백엔드 실행 중...
echo ========================================
echo.

REM web_ui 폴더에서 프로젝트 루트로 이동
cd /d "%~dp0"
cd ..

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

REM 의존성 확인
echo 백엔드 의존성 확인 중...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Flask가 설치되어 있지 않습니다. 설치 중...
    pip install -r web_ui\src\backend\requirements.txt
    if errorlevel 1 (
        echo 오류: 의존성 설치 실패
        pause
        exit /b 1
    )
)

REM PyTorch 확인
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ========================================
    echo 경고: PyTorch가 설치되어 있지 않습니다!
    echo ========================================
    echo.
    echo PyTorch를 설치해야 모델 추론이 가능합니다.
    echo.
    echo CPU 버전 설치:
    echo   pip install torch==2.4.0 torchvision==0.19.0
    echo.
    echo GPU 버전 설치 (CUDA 12.1):
    echo   pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
    echo.
    echo 지금 설치하시겠습니까? (Y/N)
    set /p INSTALL_TORCH="> "
    if /i "%INSTALL_TORCH%"=="Y" (
        echo PyTorch CPU 버전 설치 중...
        pip install torch==2.4.0 torchvision==0.19.0
        if errorlevel 1 (
            echo 오류: PyTorch 설치 실패
            echo 수동으로 설치하세요.
        )
    ) else (
        echo PyTorch 없이 계속 진행합니다. 모델 추론 기능은 작동하지 않습니다.
    )
    echo.
)

echo 백엔드 서버 시작 중...
echo http://localhost:5000 에서 실행됩니다.
echo.
python web_ui\src\backend\app.py

pause
