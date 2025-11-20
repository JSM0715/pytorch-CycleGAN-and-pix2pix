"""
실제 pix2pix 모델을 사용한 이미지 추론 모듈
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import torch
import numpy as np
from PIL import Image
from options.test_options import TestOptions
from models import create_model
from data.base_dataset import get_transform
from util.util import tensor2im


class Pix2PixInference:
    """pix2pix 모델을 사용한 이미지 추론 클래스"""
    
    def __init__(self, model_name='portrait_retouch_reverse', 
                 model_type='test',
                 direction='AtoB',
                 epoch='latest',
                 netG='unet_256',
                 norm='batch',
                 load_size=1024,
                 crop_size=1024,
                 preprocess='resize_and_crop',
                 no_dropout=True):
        """
        Args:
            model_name: 체크포인트 이름 (예: 'portrait_retouch_reverse')
            model_type: 모델 타입 ('test' 또는 'pix2pix')
            direction: 변환 방향 ('AtoB' 또는 'BtoA')
            epoch: 로드할 에포크 ('latest' 또는 숫자)
            netG: Generator 아키텍처
            norm: 정규화 방법
            load_size: 이미지 로드 크기
            crop_size: 이미지 크롭 크기
            preprocess: 전처리 방법
            no_dropout: 드롭아웃 비활성화 여부
        """
        self.model_name = model_name
        self.model_type = model_type
        self.direction = direction
        self.epoch = epoch
        self.netG = netG
        self.norm = norm
        self.load_size = load_size
        self.crop_size = crop_size
        self.preprocess = preprocess
        self.no_dropout = no_dropout
        
        self.model = None
        self.device = None
        self.transform = None
        
    def _create_options(self):
        """테스트 옵션 생성"""
        # 임시 디렉토리 생성 (없으면)
        temp_dir = PROJECT_ROOT / 'test_images' / 'temp'
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # sys.argv를 임시로 설정하여 옵션 파싱
        original_argv = sys.argv.copy()
        try:
            sys.argv = [
                'pix2pix_inference.py',  # 스크립트 이름
                '--dataroot', str(temp_dir),
                '--name', self.model_name,
                '--model', self.model_type,
                '--direction', self.direction,
                '--dataset_mode', 'single',
                '--epoch', str(self.epoch),
                '--netG', self.netG,
                '--norm', self.norm,
                '--load_size', str(self.load_size),
                '--crop_size', str(self.crop_size),
                '--preprocess', self.preprocess,
                '--no_flip',
                '--serial_batches',
                '--batch_size', '1',
                '--num_threads', '0',
                '--eval',  # eval 모드 활성화 (test.py와 동일)
            ]
            
            # 옵션 객체 생성
            test_options = TestOptions()
            opt = test_options.parse()
            
        finally:
            # sys.argv 복원
            sys.argv = original_argv
        
        # 테스트 옵션에 없는 속성들 추가 (base_model.setup에서 필요)
        if not hasattr(opt, 'continue_train'):
            opt.continue_train = False
        
        if self.no_dropout:
            opt.no_dropout = True
            
        # GPU 사용 가능 여부에 따라 디바이스 설정
        opt.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        
        return opt
    
    def load_model(self):
        """모델 로드"""
        if self.model is not None:
            return  # 이미 로드됨
            
        try:
            opt = self._create_options()
            self.device = opt.device
            
            # 체크포인트 디렉토리를 절대 경로로 변환
            if not Path(opt.checkpoints_dir).is_absolute():
                # 상대 경로인 경우 프로젝트 루트 기준으로 변환
                checkpoints_dir = PROJECT_ROOT / opt.checkpoints_dir
            else:
                checkpoints_dir = Path(opt.checkpoints_dir)
            
            # opt 객체의 checkpoints_dir도 업데이트 (모델 setup에서 사용)
            opt.checkpoints_dir = str(checkpoints_dir)
            
            # 체크포인트 파일 존재 확인
            save_dir = checkpoints_dir / opt.name
            load_filename = f"{opt.epoch}_net_G.pth"
            load_path = save_dir / load_filename
            
            print(f"[DEBUG] 체크포인트 디렉토리: {checkpoints_dir}")
            print(f"[DEBUG] 모델 디렉토리: {save_dir}")
            print(f"[DEBUG] 모델 디렉토리 존재: {save_dir.exists()}")
            print(f"[DEBUG] 체크포인트 파일: {load_path}")
            print(f"[DEBUG] 체크포인트 존재: {load_path.exists()}")
            
            if not save_dir.exists():
                raise FileNotFoundError(f"모델 디렉토리를 찾을 수 없습니다: {save_dir}")
            
            if not load_path.exists():
                # latest 파일 확인
                latest_path = save_dir / "latest_net_G.pth"
                print(f"[DEBUG] latest 체크포인트 확인: {latest_path}")
                print(f"[DEBUG] latest 체크포인트 존재: {latest_path.exists()}")
                
                if latest_path.exists() and opt.epoch != 'latest':
                    print(f"[WARNING] {load_path}를 찾을 수 없습니다. latest를 사용합니다.")
                    opt.epoch = 'latest'
                    load_path = latest_path
                elif not latest_path.exists():
                    # 사용 가능한 체크포인트 찾기
                    checkpoint_files = list(save_dir.glob('*_net_G.pth'))
                    print(f"[DEBUG] 발견된 체크포인트 파일 수: {len(checkpoint_files)}")
                    
                    if checkpoint_files:
                        # 숫자 에포크만 필터링하고 정렬
                        numeric_epochs = []
                        for cf in checkpoint_files:
                            epoch_str = cf.stem.split('_net_G')[0]
                            if epoch_str.isdigit():
                                numeric_epochs.append((int(epoch_str), epoch_str))
                        
                        if numeric_epochs:
                            # 가장 큰 에포크 사용
                            numeric_epochs.sort(reverse=True)
                            opt.epoch = numeric_epochs[0][1]
                            load_path = save_dir / f"{opt.epoch}_net_G.pth"
                            print(f"[WARNING] latest를 찾을 수 없습니다. 가장 큰 에포크 {opt.epoch}를 사용합니다.")
                        else:
                            raise FileNotFoundError(f"숫자 에포크 체크포인트를 찾을 수 없습니다: {save_dir}")
                    else:
                        raise FileNotFoundError(f"체크포인트 파일을 찾을 수 없습니다: {save_dir}")
            
            # 모델 생성
            self.model = create_model(opt)
            self.model.setup(opt)
            
            # 체크포인트가 실제로 로드되었는지 확인
            if not hasattr(self.model, 'netG') or self.model.netG is None:
                raise RuntimeError("모델이 제대로 로드되지 않았습니다.")
            
            # eval 모드 설정 (opt.eval이 True이면 이미 설정됨)
            if opt.eval:
                self.model.eval()
            else:
                self.model.eval()  # 테스트 시에는 항상 eval 모드
            
            # 이미지 변환 함수 생성
            input_nc = opt.output_nc if opt.direction == "BtoA" else opt.input_nc
            self.transform = get_transform(opt, grayscale=(input_nc == 1))
            
            print(f"모델 로드 완료: {self.model_name} (device: {self.device}, epoch: {opt.epoch})")
            
        except Exception as e:
            print(f"모델 로드 실패: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """PIL Image를 모델 입력용 Tensor로 변환"""
        if self.transform is None:
            raise RuntimeError("모델이 로드되지 않았습니다. load_model()을 먼저 호출하세요.")
        
        # RGB로 변환
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 변환 적용
        tensor = self.transform(image)
        
        # 배치 차원 추가 (1, C, H, W)
        tensor = tensor.unsqueeze(0)
        
        return tensor.to(self.device)
    
    def postprocess_image(self, tensor: torch.Tensor) -> Image.Image:
        """모델 출력 Tensor를 PIL Image로 변환
        
        Args:
            tensor: 모델 출력 텐서 (배치 차원 포함 가능)
        """
        # 디버깅: 텐서 정보 출력
        print(f"[DEBUG] postprocess_image - tensor shape: {tensor.shape}, dtype: {tensor.dtype}")
        
        # 텐서가 Variable이나 다른 래퍼에 감싸져 있을 수 있음
        if hasattr(tensor, 'data'):
            tensor = tensor.data
        if hasattr(tensor, 'cpu'):
            tensor = tensor.cpu()
        if hasattr(tensor, 'float'):
            tensor = tensor.float()
        
        # 배치 차원이 있으면 첫 번째 배치만 사용
        if len(tensor.shape) == 4:
            tensor = tensor[0]
        
        print(f"[DEBUG] postprocess_image - processed tensor shape: {tensor.shape}")
        print(f"[DEBUG] postprocess_image - tensor min: {tensor.min().item():.4f}, max: {tensor.max().item():.4f}, mean: {tensor.mean().item():.4f}")
        
        # (C, H, W) -> (H, W, C)로 transpose
        if tensor.shape[0] == 1:  # grayscale to RGB
            tensor = tensor.repeat(3, 1, 1)
        
        image_numpy = tensor.numpy()
        image_numpy = np.transpose(image_numpy, (1, 2, 0))
        
        # [-1, 1] 범위를 [0, 255]로 변환
        image_numpy = (image_numpy + 1.0) / 2.0 * 255.0
        image_numpy = np.clip(image_numpy, 0, 255).astype(np.uint8)
        
        print(f"[DEBUG] postprocess_image - image_numpy shape: {image_numpy.shape}, dtype: {image_numpy.dtype}")
        print(f"[DEBUG] postprocess_image - image_numpy min: {image_numpy.min()}, max: {image_numpy.max()}, mean: {image_numpy.mean():.2f}")
        
        # PIL Image로 변환
        image_pil = Image.fromarray(image_numpy, mode='RGB')
        
        print(f"[DEBUG] postprocess_image - PIL Image size: {image_pil.size}, mode: {image_pil.mode}")
        
        return image_pil
    
    def infer(self, image: Image.Image) -> Image.Image:
        """
        이미지에 모델 추론 수행 (test.py와 동일한 방식)
        
        Args:
            image: 입력 PIL Image
            
        Returns:
            변환된 PIL Image
        """
        if self.model is None:
            self.load_model()
        
        # 임시 디렉토리에 이미지 저장 (test.py가 데이터셋에서 읽을 수 있도록)
        import tempfile
        import uuid
        
        temp_dir = PROJECT_ROOT / 'test_images' / 'web_ui_temp'
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 고유한 파일명 생성
        temp_image_name = f"web_ui_{uuid.uuid4().hex[:8]}.png"
        temp_image_path = temp_dir / temp_image_name
        
        # 이미지 저장
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(temp_image_path)
        
        try:
            # test.py와 동일한 방식으로 데이터셋 생성
            from data import create_dataset
            
            # 옵션 재생성 (dataroot를 임시 디렉토리로 설정)
            # 주의: 이미 모델이 로드되어 있으므로, 옵션만 재생성 (모델은 재생성하지 않음)
            opt = self._create_options()
            opt.dataroot = str(temp_dir)
            opt.num_test = 1  # 단일 이미지만 처리
            
            # 체크포인트 경로 확인 (디버깅)
            save_dir = Path(opt.checkpoints_dir) / opt.name
            load_filename = f"{opt.epoch}_net_G.pth"
            load_path = save_dir / load_filename
            print(f"[DEBUG] 체크포인트 경로 확인: {load_path}")
            print(f"[DEBUG] 체크포인트 존재: {load_path.exists()}")
            if not load_path.exists():
                # latest 파일 확인
                latest_path = save_dir / "latest_net_G.pth"
                print(f"[DEBUG] latest 체크포인트 확인: {latest_path}")
                print(f"[DEBUG] latest 체크포인트 존재: {latest_path.exists()}")
                if latest_path.exists() and opt.epoch != 'latest':
                    print(f"[WARNING] {load_path}를 찾을 수 없습니다. latest를 사용합니다.")
                    opt.epoch = 'latest'
            
            # 데이터셋 생성
            dataset = create_dataset(opt)
            
            # 데이터셋에서 첫 번째 이미지 가져오기
            data = next(iter(dataset))
            
            # 모델 입력 설정
            self.model.set_input(data)
            
            # 추론 실행 (test.py와 동일)
            self.model.test()
            
            # 결과 가져오기
            visuals = self.model.get_current_visuals()
            print(f"[DEBUG] infer - visuals keys: {list(visuals.keys())}")
            
            # test.py는 save_images를 사용하지만, 우리는 직접 처리
            # fake 또는 fake_B 이미지 가져오기
            if 'fake' in visuals:
                output_tensor = visuals['fake']
                print(f"[DEBUG] infer - using 'fake', shape: {output_tensor.shape}, dtype: {output_tensor.dtype}")
            elif 'fake_B' in visuals:
                output_tensor = visuals['fake_B']
                print(f"[DEBUG] infer - using 'fake_B', shape: {output_tensor.shape}, dtype: {output_tensor.dtype}")
            else:
                available_keys = list(visuals.keys())
                print(f"[ERROR] infer - available keys: {available_keys}")
                for key, value in visuals.items():
                    if isinstance(value, torch.Tensor):
                        print(f"[ERROR] infer - {key}: shape={value.shape}, dtype={value.dtype}, min={value.min().item():.4f}, max={value.max().item():.4f}")
                raise ValueError(f"모델 출력에서 결과 이미지를 찾을 수 없습니다. 사용 가능한 키: {available_keys}")
            
            # test.py의 save_images와 동일한 방식으로 변환
            # tensor2im 함수를 직접 구현 (test.py와 동일)
            print(f"[DEBUG] infer - output_tensor shape: {output_tensor.shape}, dtype: {output_tensor.dtype}")
            print(f"[DEBUG] infer - tensor min: {output_tensor.min().item():.4f}, max: {output_tensor.max().item():.4f}, mean: {output_tensor.mean().item():.4f}")
            
            # tensor2im과 동일한 로직
            # 텐서를 CPU로 이동하고 numpy로 변환
            if hasattr(output_tensor, 'data'):
                image_tensor = output_tensor.data
            else:
                image_tensor = output_tensor
            
            # 배치 차원 처리
            if len(image_tensor.shape) == 4:
                image_tensor = image_tensor[0]  # 첫 번째 배치만 사용
            elif len(image_tensor.shape) == 3:
                pass  # 이미 배치 차원이 없음
            else:
                raise ValueError(f"Unexpected tensor shape: {image_tensor.shape}")
            
            # CPU로 이동하고 float로 변환 후 numpy로 변환
            image_numpy = image_tensor.cpu().float().numpy()
            
            # grayscale to RGB
            if image_numpy.shape[0] == 1:
                image_numpy = np.tile(image_numpy, (3, 1, 1))
            
            # (C, H, W) -> (H, W, C)로 transpose
            image_numpy = np.transpose(image_numpy, (1, 2, 0))
            
            # [-1, 1] 범위를 [0, 255]로 변환
            image_numpy = (image_numpy + 1.0) / 2.0 * 255.0
            image_numpy = np.clip(image_numpy, 0, 255).astype(np.uint8)
            
            print(f"[DEBUG] infer - image_numpy shape: {image_numpy.shape}, dtype: {image_numpy.dtype}")
            print(f"[DEBUG] infer - image_numpy min: {image_numpy.min()}, max: {image_numpy.max()}, mean: {image_numpy.mean():.2f}")
            
            # PIL Image로 변환
            output_image = Image.fromarray(image_numpy, mode='RGB')
            
            print(f"[DEBUG] infer - final PIL Image: size={output_image.size}, mode={output_image.mode}")
            
            return output_image
            
        finally:
            # 임시 파일 정리
            try:
                if temp_image_path.exists():
                    temp_image_path.unlink()
            except:
                pass
    
    def get_model_info(self):
        """모델 정보 반환"""
        return {
            'name': self.model_name,
            'type': self.model_type,
            'direction': self.direction,
            'epoch': self.epoch,
            'device': str(self.device) if self.device else 'not loaded',
            'loaded': self.model is not None
        }

