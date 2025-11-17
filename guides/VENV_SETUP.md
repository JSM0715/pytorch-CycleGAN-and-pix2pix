# venv를 사용한 환경 설정 가이드

이 문서는 Python venv를 사용하여 프로젝트 환경을 설정하는 방법을 설명합니다.

## Windows에서 venv 사용하기

### 1. 가상환경 생성

```powershell
# 프로젝트 루트 디렉토리에서 실행
python -m venv venv
```

### 2. 가상환경 활성화

```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat
```

활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.

### 3. PyTorch 설치

GPU가 있는 경우 (CUDA 12.1):
```powershell
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
```

CPU만 사용하는 경우:
```powershell
pip install torch==2.4.0 torchvision==0.19.0
```

### 4. 나머지 패키지 설치

```powershell
pip install -r requirements.txt
```

### 5. 설치 확인

```powershell
python -c "import torch; print(torch.__version__)"
python -c "import torchvision; print(torchvision.__version__)"
```

## Linux/macOS에서 venv 사용하기

### 1. 가상환경 생성

```bash
# 프로젝트 루트 디렉토리에서 실행
python3 -m venv venv
```

### 2. 가상환경 활성화

```bash
source venv/bin/activate
```

활성화되면 프롬프트 앞에 `(venv)`가 표시됩니다.

### 3. PyTorch 설치

GPU가 있는 경우 (CUDA 12.1):
```bash
pip install torch==2.4.0 torchvision==0.19.0 --index-url https://download.pytorch.org/whl/cu121
```

CPU만 사용하는 경우:
```bash
pip install torch==2.4.0 torchvision==0.19.0
```

### 4. 나머지 패키지 설치

```bash
pip install -r requirements.txt
```

### 5. 설치 확인

```bash
python -c "import torch; print(torch.__version__)"
python -c "import torchvision; print(torchvision.__version__)"
```

## 사용 예시

### 가상환경 활성화 후 학습 실행

```bash
# 가상환경 활성화 (위의 방법 중 하나 사용)
# Windows PowerShell: .\venv\Scripts\Activate.ps1
# Linux/macOS: source venv/bin/activate

# CycleGAN 학습
python train.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan --use_wandb

# 테스트
python test.py --dataroot ./datasets/maps --name maps_cyclegan --model cycle_gan
```

### 가상환경 비활성화

```bash
deactivate
```

## 주의사항

1. **Python 버전**: Python 3.11을 권장합니다 (Python 3.8 이상 필요)
2. **CUDA 버전**: GPU를 사용하는 경우, 시스템에 설치된 CUDA 버전에 맞는 PyTorch를 설치해야 합니다
3. **.gitignore**: `venv/` 폴더는 일반적으로 .gitignore에 추가되어 있습니다

## 문제 해결

### PowerShell에서 실행 정책 오류 발생 시

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### pip 업그레이드

```bash
python -m pip install --upgrade pip
```


