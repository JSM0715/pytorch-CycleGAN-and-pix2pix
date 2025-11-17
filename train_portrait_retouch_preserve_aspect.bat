@echo off
chcp 65001 >nul
REM 종횡비 유지하면서 학습하는 스크립트

echo ========================================
echo 인물사진 복원 모델 학습 (종횡비 유지)
echo ========================================
echo.

REM 종횡비 유지 옵션:
REM --preprocess scale_width_and_crop: 너비를 load_size로 조정 후 crop_size로 크롭
REM --preprocess scale_width: 너비만 조정하고 크롭 없음 (완전한 종횡비 유지)

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
    --lambda_L1 500.0 ^
    --lr 0.0001

pause

