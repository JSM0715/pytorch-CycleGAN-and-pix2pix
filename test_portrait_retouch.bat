@echo off
REM 인물 보정 테스트 스크립트 (1024x1024)

python test.py ^
  --dataroot ./test_images/test ^
  --name portrait_retouch_reverse ^
  --model test ^
  --direction AtoB ^
  --dataset_mode single ^
  --epoch latest ^
  --netG unet_256 ^
  --norm batch ^
  --load_size 1024 ^
  --crop_size 1024 ^
  --preprocess resize_and_crop

pause

