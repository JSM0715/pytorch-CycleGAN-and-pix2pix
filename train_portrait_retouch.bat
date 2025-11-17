@echo off
REM 인물 보정 후 -> 보정 전 변환 학습 스크립트

python train.py ^
    --dataroot ./portrait_retouch ^
    --name portrait_retouch_reverse ^
    --model pix2pix ^
    --direction AtoB ^
    --batch_size 1 ^
    --load_size 512 ^
    --crop_size 512 ^
    --n_epochs 200 ^
    --n_epochs_decay 200 ^
    --display_freq 50 ^
    --print_freq 10 ^
    --save_epoch_freq 10 ^
    --use_wandb

pause

