"""이미지-이미지 변환을 위한 범용 테스트 스크립트.

train.py로 모델을 훈련시킨 후, 이 스크립트를 사용하여 모델을 테스트할 수 있습니다.
'--checkpoints_dir'에서 저장된 모델을 로드하고 결과를 '--results_dir'에 저장합니다.

옵션에 따라 모델과 데이터셋을 먼저 생성합니다. 일부 파라미터는 하드코딩됩니다.
그런 다음 '--num_test' 이미지에 대해 추론을 실행하고 결과를 HTML 파일로 저장합니다.

예시 (먼저 모델을 훈련시키거나 사전 훈련된 모델을 다운로드해야 합니다):
    CycleGAN 모델 테스트 (양방향):
        python test.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan

    CycleGAN 모델 테스트 (한 방향만):
        python test.py --dataroot datasets/horse2zebra/testA --name horse2zebra_pretrained --model test --no_dropout

    '--model test' 옵션은 CycleGAN 결과를 한 방향으로만 생성하는 데 사용됩니다.
    이 옵션은 자동으로 '--dataset_mode single'을 설정하여 한 세트의 이미지만 로드합니다.
    반대로 '--model cycle_gan'을 사용하면 양방향으로 결과를 로드하고 생성해야 하며,
    때로는 불필요할 수 있습니다. 결과는 ./results/에 저장됩니다.
    '--results_dir <directory_path_to_save_result>'를 사용하여 결과 디렉토리를 지정할 수 있습니다.

    pix2pix 모델 테스트:
        python test.py --dataroot ./datasets/facades --name facades_pix2pix --model pix2pix --direction BtoA

더 많은 테스트 옵션은 options/base_options.py와 options/test_options.py를 참조하세요.
훈련 및 테스트 팁: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/tips.md
자주 묻는 질문: https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix/blob/master/docs/qa.md
"""

import os
from pathlib import Path
from options.test_options import TestOptions  # 테스트 옵션 파서
from data import create_dataset  # 데이터셋 생성 함수
from models import create_model  # 모델 생성 함수
from util.visualizer import save_images  # 이미지 저장 함수
from util import html  # HTML 생성 유틸리티
import torch

# wandb 라이브러리 임포트 시도 (선택적)
try:
    import wandb
except ImportError:
    print('Warning: wandb package cannot be found. The option "--use_wandb" will result in error.')


if __name__ == "__main__":
    # 테스트 옵션 파싱
    opt = TestOptions().parse()
    
    # GPU 사용 가능 여부에 따라 디바이스 설정
    opt.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    # 테스트를 위해 일부 파라미터 하드코딩
    opt.num_threads = 0  # 테스트 코드는 num_threads = 0만 지원
    opt.batch_size = 1  # 테스트 코드는 batch_size = 1만 지원
    opt.serial_batches = True  # 데이터 셔플링 비활성화; 무작위로 선택된 이미지 결과가 필요하면 이 줄을 주석 처리
    opt.no_flip = True  # 이미지 뒤집기 비활성화; 뒤집힌 이미지 결과가 필요하면 이 줄을 주석 처리
    
    # 옵션에 따라 데이터셋 생성
    dataset = create_dataset(opt)
    
    # 옵션에 따라 모델 생성
    model = create_model(opt)
    
    # 정규 설정: 네트워크 로드 및 출력, 스케줄러 생성
    model.setup(opt)

    # 결과를 저장할 웹 디렉토리 생성
    web_dir = Path(opt.results_dir) / opt.name / f"{opt.phase}_{opt.epoch}"
    if opt.load_iter > 0:  # load_iter는 기본값이 0
        web_dir = Path(f"{web_dir}_iter{opt.load_iter}")
    print(f"creating web directory {web_dir}")
    
    # HTML 웹페이지 객체 생성
    webpage = html.HTML(web_dir, f"Experiment = {opt.name}, Phase = {opt.phase}, Epoch = {opt.epoch}")
    
    # eval 모드로 테스트. 이는 batchnorm과 dropout 같은 레이어에만 영향을 줍니다.
    # [pix2pix]: 원본 pix2pix에서 batchnorm과 dropout을 사용합니다. eval() 모드 유무로 실험할 수 있습니다.
    # [CycleGAN]: CycleGAN은 dropout 없이 instancenorm을 사용하므로 영향을 주지 않아야 합니다.
    if opt.eval:
        model.eval()
    
    # 데이터셋의 각 이미지에 대해 추론 수행
    for i, data in enumerate(dataset):
        if i >= opt.num_test:  # opt.num_test 이미지에만 모델 적용
            break
        
        # 데이터 로더에서 데이터 언패킹
        model.set_input(data)
        
        # 추론 실행
        model.test()
        
        # 이미지 결과 가져오기
        visuals = model.get_current_visuals()
        
        # 이미지 경로 가져오기
        img_path = model.get_image_paths()
        
        # 5개마다 진행 상황 출력 및 HTML 파일에 이미지 저장
        if i % 5 == 0:
            print(f"processing ({i:04d})-th image... {img_path}")
        
        # 이미지를 HTML 웹페이지에 저장
        save_images(webpage, visuals, img_path, aspect_ratio=opt.aspect_ratio, width=opt.display_winsize)
    
    # HTML 파일 저장
    webpage.save()
