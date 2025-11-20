# AI 모델 구현 가이드

이 문서는 Python 프로젝트에서 실제 AI 모델을 구현하는 방법을 설명합니다.

## 📁 파일 구조

```
backend/
├── app.py                      # Flask 메인 서버 (수정 불필요)
├── models_interface.py         # 모델 인터페이스 정의 (수정 불필요)
├── model_implementations.py    # 모델 구현 (여기를 수정하세요!)
└── requirements.txt            # Python 패키지 목록
```

## 🎯 구현해야 할 것

### 1. 각 모델 클래스의 3가지 메서드

각 AI 모델 클래스(`GFPGANModel`, `CodeFormerModel`, `RestoreFormerModel`, `RealESRGANModel`)에서 다음 메서드를 구현하세요:

#### `load_model()` - 모델 로드
```python
def load_model(self) -> None:
    """모델 가중치를 메모리에 로드"""
    from gfpgan import GFPGANer
    
    self.model = GFPGANer(
        model_path='weights/GFPGANv1.4.pth',
        upscale=2,
        arch='clean',
        channel_multiplier=2,
        device=self.device
    )
```

#### `restore()` - 이미지 복원
```python
def restore(self, image: Image.Image, **kwargs) -> Image.Image:
    """실제 이미지 복원 수행"""
    import numpy as np
    
    # PIL Image → numpy array
    input_img = np.array(image)
    
    # 모델 실행
    _, _, restored_img = self.model.enhance(
        input_img,
        has_aligned=False,
        paste_back=True
    )
    
    # numpy array → PIL Image
    return Image.fromarray(restored_img)
```

#### `get_model_info()` - 모델 정보
```python
def get_model_info(self) -> Dict[str, Any]:
    """모델 메타데이터 반환 (이미 구현됨)"""
    return {
        'name': 'GFPGAN',
        'version': '1.4',
        'description': '일반적인 얼굴 복원 모델',
        'supported_formats': ['jpg', 'jpeg', 'png', 'bmp'],
        'max_resolution': (2048, 2048)
    }
```

## 📝 구현 예제

### GFPGAN 구현 예제

```python
class GFPGANModel(RestorationModel):
    def load_model(self) -> None:
        """GFPGAN 모델 로드"""
        try:
            from gfpgan import GFPGANer
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
            
            # 배경 업샘플러 (선택사항)
            bg_upsampler = RealESRGANer(
                scale=2,
                model_path='weights/RealESGAN_x2plus.pth',
                model=RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, 
                             num_block=23, num_grow_ch=32, scale=2),
                tile=400,
                tile_pad=10,
                pre_pad=0,
                half=True if self.device == 'cuda' else False
            )
            
            # GFPGAN 로드
            self.model = GFPGANer(
                model_path='weights/GFPGANv1.4.pth',
                upscale=2,
                arch='clean',
                channel_multiplier=2,
                bg_upsampler=bg_upsampler,
                device=self.device
            )
            
            print("[GFPGAN] 모델 로드 완료")
            
        except Exception as e:
            print(f"[GFPGAN] 모델 로드 실패: {e}")
            raise
    
    def restore(self, image: Image.Image, **kwargs) -> Image.Image:
        """GFPGAN으로 이미지 복원"""
        import numpy as np
        
        # 전처리
        image = self.preprocess(image)
        
        # PIL → numpy
        input_img = np.array(image)
        
        # 복원 수행
        cropped_faces, restored_faces, restored_img = self.model.enhance(
            input_img,
            has_aligned=False,
            only_center_face=False,
            paste_back=True,
            weight=kwargs.get('face_enhance', 0.5)
        )
        
        # numpy → PIL
        restored_image = Image.fromarray(restored_img)
        
        # 후처리
        return self.postprocess(restored_image)
```

### CodeFormer 구현 예제

```python
class CodeFormerModel(RestorationModel):
    def load_model(self) -> None:
        """CodeFormer 모델 로드"""
        try:
            from codeformer import CodeFormer
            import torch
            
            self.model = CodeFormer(
                dim_embd=512,
                codebook_size=1024,
                n_head=8,
                n_layers=9,
                connect_list=['32', '64', '128', '256']
            ).to(self.device)
            
            # 가중치 로드
            checkpoint = torch.load('weights/codeformer.pth', 
                                  map_location=self.device)
            self.model.load_state_dict(checkpoint['params'])
            self.model.eval()
            
            print("[CodeFormer] 모델 로드 완료")
            
        except Exception as e:
            print(f"[CodeFormer] 모델 로드 실패: {e}")
            raise
    
    def restore(self, image: Image.Image, **kwargs) -> Image.Image:
        """CodeFormer로 이미지 복원"""
        import numpy as np
        import torch
        from torchvision.transforms.functional import normalize
        
        # 전처리
        image = self.preprocess(image)
        
        # PIL → Tensor
        img_np = np.array(image) / 255.0
        img_tensor = torch.from_numpy(img_np).float().permute(2, 0, 1).unsqueeze(0)
        img_tensor = normalize(img_tensor, [0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        img_tensor = img_tensor.to(self.device)
        
        # 복원 수행
        with torch.no_grad():
            fidelity = kwargs.get('codeformer_fidelity', 0.5)
            output = self.model(img_tensor, w=fidelity)[0]
        
        # Tensor → PIL
        output = output.squeeze(0).permute(1, 2, 0).cpu().numpy()
        output = ((output + 1) / 2 * 255).clip(0, 255).astype(np.uint8)
        restored_image = Image.fromarray(output)
        
        return self.postprocess(restored_image)
```

## 🔧 설정 파라미터

`RestorationConfig` 클래스를 통해 전달되는 파라미터들:

```python
config = RestorationConfig(
    scale=2,                      # 업스케일 배율
    face_enhance=True,            # 얼굴 향상 활성화
    bg_enhance=False,             # 배경 향상 활성화
    denoise_strength=0.5,         # 노이즈 제거 강도 (0.0 ~ 1.0)
    codeformer_fidelity=0.5,      # CodeFormer 충실도 (0.0 ~ 1.0)
    max_image_size=2048           # 최대 이미지 크기
)

# 모델에 전달
restored_image = model.restore(image, **config.to_dict())
```

## 📦 필요한 패키지

각 모델에 필요한 Python 패키지를 `requirements.txt`에 추가하세요:

### GFPGAN
```
gfpgan
basicsr
facexlib
realesrgan
```

### CodeFormer
```
codeformer
torch
torchvision
```

### RestoreFormer
```
restoreformer
torch
```

### Real-ESRGAN
```
realesrgan
basicsr
```

## 🚀 모델 가중치 다운로드

각 모델의 가중치 파일을 다운로드하여 `weights/` 디렉토리에 저장하세요:

```bash
mkdir weights
cd weights

# GFPGAN
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth

# CodeFormer
wget https://github.com/sczhou/CodeFormer/releases/download/v0.1.0/codeformer.pth

# Real-ESRGAN
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESGAN_x2plus.pth
```

## 🧪 테스트

모델 구현 후 테스트:

```python
# test_models.py
from PIL import Image
from models_interface import ModelFactory

# 모델 생성
model = ModelFactory.create_model('gfpgan')

# 이미지 로드
image = Image.open('test.jpg')

# 복원
restored = model.restore(image)

# 저장
restored.save('restored.jpg')

print(model.get_model_info())
```

## 💡 팁

1. **GPU 사용**: `device='cuda'`로 설정하면 GPU 가속 사용
2. **메모리 최적화**: 큰 이미지는 타일 단위로 처리
3. **에러 처리**: try-except로 에러 핸들링 추가
4. **로깅**: 처리 진행 상황을 로그로 출력

## 📞 API 엔드포인트

구현이 완료되면 다음 API들이 자동으로 작동합니다:

- `POST /api/restore` - 이미지 복원
- `GET /api/models` - 사용 가능한 모델 목록
- `GET /api/health` - 서버 상태 확인

## 🔄 현재 상태

현재는 임시 구현(`_temporary_enhance()`)이 동작하고 있습니다.
실제 AI 모델을 구현하면 자동으로 대체됩니다.

## ❓ 자주 묻는 질문

**Q: 모델 파일이 너무 큽니다.**  
A: Git LFS를 사용하거나, 서버에서 직접 다운로드하도록 구현하세요.

**Q: 여러 모델을 동시에 사용하면 메모리가 부족합니다.**  
A: `model_cache`에서 필요 없는 모델을 제거하거나, lazy loading을 구현하세요.

**Q: 새로운 모델을 추가하고 싶습니다.**  
A: `RestorationModel`을 상속받아 구현 후 `register_all_models()`에서 등록하세요.
