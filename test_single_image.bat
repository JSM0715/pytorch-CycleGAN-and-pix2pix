@echo off
REM 단일 이미지 모드로 테스트 (전체 크기 결과)

python test.py ^
    --dataroot ./test_images/test ^
    --name portrait_retouch_reverse ^
    --model test ^
    --direction AtoB ^
    --dataset_mode single ^
    --epoch latest ^
    --netG unet_256 ^
    --norm batch

pause

