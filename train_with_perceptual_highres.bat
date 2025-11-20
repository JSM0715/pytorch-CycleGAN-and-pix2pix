@echo off
REM 인물 보정 훈련 스크립트 (perceptual loss, 고해상도, lsgan)

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
  --lambda_L1 500.0 ^
  --lambda_perceptual 10.0 ^
  --use_perceptual ^
  --gan_mode lsgan ^
  --lr 0.0001

pause

