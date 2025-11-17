# PyTorch 설치 가이드

백엔드 서버를 실행하려면 PyTorch가 필요합니다.

## 빠른 설치

### CPU 버전 (가장 간단)
```bash
pip install torch==2.4.0 torchvision==0.19.0
```

### GPU 버전 (CUDA 12.1)
```bash
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
```

## 설치 확인

```bash
python -c "import torch; print(f'PyTorch {torch.__version__}')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## 다른 CUDA 버전

PyTorch 공식 사이트에서 맞는 버전을 확인하세요:
https://pytorch.org/get-started/locally/

## 문제 해결

### 설치가 느린 경우
- pip 캐시 사용: `pip install --cache-dir .pip_cache torch==2.4.0 torchvision==0.19.0`
- 또는 conda 사용: `conda install pytorch torchvision -c pytorch`

### 메모리 부족 오류
- CPU 버전 사용 (더 작음)
- 또는 가상환경에서 설치

