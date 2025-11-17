@echo off
chcp 65001 >nul
REM 보정 영역 주변 흐림 문제 해결을 위한 학습 스크립트

echo ========================================
echo 인물사진 복원 모델 학습 (흐림 문제 해결)
echo ========================================
echo.
echo 방법 1: Perceptual Loss 사용 (권장)
echo 방법 2: L1 Loss 감소 + LSGAN
echo.

REM 방법 1: Perceptual Loss 사용
echo [방법 1] Perceptual Loss를 사용한 학습 시작...
python train.py ^
    --dataroot ./portrait_retouch ^
    --name portrait_retouch_reverse ^
    --model pix2pix_with_perceptual ^
    --direction AtoB ^
    --batch_size 1 ^
    --preprocess scale_width_and_crop ^
    --load_size 1024 ^
    --crop_size 1024 ^
    --n_epochs 1000 ^
    --n_epochs_decay 1000 ^
    --lambda_L1 100.0 ^
    --lambda_perceptual 10.0 ^
    --use_perceptual ^
    --gan_mode lsgan ^
    --lr 0.0001

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [방법 1 실패] 방법 2로 시도합니다...
    echo.
    REM 방법 2: L1 Loss 감소 + LSGAN
    python train.py ^
        --dataroot ./portrait_retouch ^
        --name portrait_retouch_reverse ^
        --model pix2pix ^
        --direction AtoB ^
        --batch_size 1 ^
        --preprocess scale_width_and_crop ^
        --load_size 1024 ^
        --crop_size 1024 ^
        --n_epochs 1000 ^
        --n_epochs_decay 1000 ^
        --lambda_L1 50.0 ^
        --gan_mode lsgan ^
        --n_layers_D 4 ^
        --lr 0.0001
)

pause

