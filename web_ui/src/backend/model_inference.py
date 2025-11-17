"""
모델 추론을 위한 유틸리티 함수
"""
import sys
from pathlib import Path
import torch
from PIL import Image
import numpy as np
from io import BytesIO
import tempfile
import os

# 프로젝트 루트를 sys.path에 추가
# model_inference.py 위치: web_ui/src/backend/model_inference.py
# 상위 4단계: web_ui/src/backend -> web_ui/src -> web_ui -> 프로젝트 루트
_current_file = Path(__file__).resolve()
PROJECT_ROOT = _current_file.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 디버깅용 로그
print(f"[DEBUG] model_inference.py location: {_current_file}")
print(f"[DEBUG] PROJECT_ROOT: {PROJECT_ROOT}")
print(f"[DEBUG] PROJECT_ROOT exists: {PROJECT_ROOT.exists()}")
print(f"[DEBUG] options folder exists: {(PROJECT_ROOT / 'options').exists()}")

from options.test_options import TestOptions
from models import create_model
from util.util import tensor2im


def create_inference_options(
    image_path: str,
    model_name: str = 'portrait_retouch_reverse',
    epoch: str = 'latest',
    direction: str = 'AtoB',
    netG: str = 'unet_256',
    norm: str = 'batch',
    load_size: int = 1024,
    crop_size: int = 1024,
    preprocess: str = 'resize_and_crop'
):
    """추론을 위한 옵션 생성"""
    import argparse
    import sys
    
    # TestOptions를 사용하여 옵션 생성
    # gather_options를 사용하면 모델 클래스의 modify_commandline_options가 자동으로 호출됨
    test_opt = TestOptions()
    
    # 임시로 sys.argv를 백업하고 설정
    old_argv = sys.argv
    try:
        # 명령줄 인자 설정
        sys.argv = [
            'model_inference.py',
            '--dataroot', str(Path(image_path).parent),
            '--name', model_name,
            '--model', 'test',
            '--direction', direction,
            '--dataset_mode', 'single',
            '--epoch', epoch,
            '--netG', netG,
            '--norm', norm,
            '--load_size', str(load_size),
            '--crop_size', str(crop_size),
            '--preprocess', preprocess,
            '--no_dropout',
            '--eval',
            '--num_threads', '0',
            '--batch_size', '1',
            '--serial_batches',
            '--no_flip',
            '--checkpoints_dir', str(PROJECT_ROOT / 'checkpoints'),
            '--model_suffix', '',  # test 모델에서 필요한 옵션
        ]
        
        # gather_options를 사용하여 모든 옵션 수집 (모델 클래스의 modify_commandline_options 포함)
        opt = test_opt.parse()
        
        # 추가 설정
        opt.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        return opt
    finally:
        # sys.argv 복원
        sys.argv = old_argv


def run_inference(
    image_data: bytes,
    model_name: str = 'portrait_retouch_reverse',
    epoch: str = 'latest',
    direction: str = 'AtoB',
    netG: str = 'unet_256',
    norm: str = 'batch',
    load_size: int = 1024,
    crop_size: int = 1024,
    preprocess: str = 'resize_and_crop'
) -> Image.Image:
    """
    이미지에 모델 추론 수행
    
    Args:
        image_data: 이미지 바이트 데이터
        model_name: 모델 이름
        epoch: 에포크 번호 또는 'latest'
        direction: 변환 방향 (AtoB 또는 BtoA)
        netG: Generator 네트워크 타입
        norm: 정규화 타입
        load_size: 로드 크기
        crop_size: 크롭 크기
        preprocess: 전처리 방법
    
    Returns:
        PIL Image: 추론 결과 이미지
    """
    # 임시 디렉토리 생성 및 이미지 저장
    # SingleDataset은 dataroot 디렉토리에서 모든 이미지를 찾으므로,
    # 임시 디렉토리를 만들고 그 안에 이미지를 저장해야 함
    temp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(temp_dir, 'input.png')
    
    try:
        # 이미지 데이터를 임시 파일로 저장
        with open(tmp_path, 'wb') as f:
            f.write(image_data)
        
        print(f"[DEBUG] Saved input image to: {tmp_path}")
        print(f"[DEBUG] Temp directory: {temp_dir}")
        
        # 옵션 생성 (dataroot는 임시 디렉토리)
        opt = create_inference_options(
            image_path=tmp_path,
            model_name=model_name,
            epoch=epoch,
            direction=direction,
            netG=netG,
            norm=norm,
            load_size=load_size,
            crop_size=crop_size,
            preprocess=preprocess
        )
        
        # dataroot를 임시 디렉토리로 설정
        opt.dataroot = temp_dir
        
        print(f"[DEBUG] Inference options:")
        print(f"  - model_name: {model_name}")
        print(f"  - epoch: {epoch}")
        print(f"  - direction: {direction}")
        print(f"  - dataroot: {opt.dataroot}")
        print(f"  - checkpoints_dir: {opt.checkpoints_dir}")
        print(f"  - model: {opt.model}")
        print(f"  - dataset_mode: {opt.dataset_mode}")
        
        # test.py와 동일한 방식으로 모델 생성 및 설정
        print(f"[DEBUG] Creating dataset...")
        from data import create_dataset
        dataset = create_dataset(opt)
        print(f"[DEBUG] Dataset created with {len(dataset)} images")
        
        print(f"[DEBUG] Creating model...")
        model = create_model(opt)
        print(f"[DEBUG] Setting up model...")
        model.setup(opt)  # 모델 로드 및 설정
        
        # eval 모드 설정 (opt.eval이 True인 경우)
        if opt.eval:
            model.eval()
            print(f"[DEBUG] Model set to eval mode")
        
        print(f"[DEBUG] Model loaded successfully")
        
        # 추론 수행 (test.py와 동일한 방식)
        print(f"[DEBUG] Running inference...")
        result_image = None
        
        for i, data in enumerate(dataset):
            if i >= 1:  # 단일 이미지이므로 한 번만 실행
                break
                
            print(f"[DEBUG] Processing image {i+1}")
            print(f"[DEBUG] Input data keys: {list(data.keys())}")
            if 'A' in data:
                print(f"[DEBUG] Input tensor shape: {data['A'].shape}")
                print(f"[DEBUG] Input tensor min/max: {data['A'].min().item():.3f} / {data['A'].max().item():.3f}")
            
            model.set_input(data)
            model.test()
            visuals = model.get_current_visuals()
            
            print(f"[DEBUG] Visuals keys: {list(visuals.keys())}")
            
            # TestModel은 visual_names = ["real", "fake"]를 사용
            if 'fake' in visuals:
                fake_tensor = visuals['fake']
                print(f"[DEBUG] Using 'fake' key, shape: {fake_tensor.shape}")
            elif 'fake_B' in visuals:
                fake_tensor = visuals['fake_B']
                print(f"[DEBUG] Using 'fake_B' key, shape: {fake_tensor.shape}")
            else:
                available_keys = list(visuals.keys())
                print(f"[ERROR] Available visual keys: {available_keys}")
                raise ValueError(f"추론 결과를 찾을 수 없습니다. 사용 가능한 키: {available_keys}")
            
            # util.tensor2im을 사용하여 텐서를 numpy 배열로 변환
            result_numpy = tensor2im(fake_tensor)
            print(f"[DEBUG] Result numpy shape: {result_numpy.shape}, dtype: {result_numpy.dtype}")
            
            # numpy 배열을 PIL Image로 변환
            result_image = Image.fromarray(result_numpy)
            print(f"[DEBUG] Result PIL Image size: {result_image.size}, mode: {result_image.mode}")
        
        if result_image is None:
            raise ValueError("추론 결과를 생성할 수 없습니다")
        
        return result_image
    
    finally:
        # 임시 디렉토리 삭제
        import shutil
        if os.path.exists(temp_dir):
            print(f"[DEBUG] Cleaning up temp directory: {temp_dir}")
            shutil.rmtree(temp_dir)

