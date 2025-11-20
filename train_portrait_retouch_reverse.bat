@echo off
REM 인물 보정 후 -> 보정 전 변환 학습 스크립트 (1024x1024, continue_train)

python train.py ^
    --dataroot ./portrait_retouch ^
    --name portrait_retouch_reverse ^
    --model pix2pix ^
    --direction AtoB ^
    --continue_train ^
    --batch_size 1 ^
    --load_size 1024 ^
    --crop_size 1024 ^
    --n_epochs 200 ^
    --n_epochs_decay 200

pause

