# 인물 보정 후 → 보정 전 변환 모델 사용 가이드

## 목차

1. [환경구성](#1-환경구성)
2. [합쳐진 이미지 생성](#2-합쳐진-이미지-생성)
3. [학습하기](#3-학습하기)
4. [학습된 모델 사용](#4-학습된-모델-사용)

---

## 1. 환경구성

### 1.1 Conda 환경 생성

```bash
conda env create -f environment.yml
```

**파라미터 설명**:
- `-f environment.yml`: 환경 설정 파일 경로
  - 예: `environment.yml` (프로젝트 루트에 있는 파일)
  - 포함된 내용: Python 3.11, PyTorch 2.4.0, torchvision 0.19.0, CUDA 12.1, numpy, scikit-image 등

**설명**:
- `environment.yml`: 프로젝트에 필요한 모든 패키지와 버전이 정의된 파일
- Conda를 사용하면 PyTorch와 CUDA를 포함한 모든 의존성을 한 번에 설치할 수 있음

### 1.2 Conda 환경 활성화

```bash
conda activate pytorch-img2img
```

**파라미터 설명**:
- `pytorch-img2img`: 환경 이름 (environment.yml에 정의된 이름)
  - 예: `pytorch-img2img`

**설명**:
- 환경 활성화 후 프롬프트 앞에 `(pytorch-img2img)`가 표시됨
- 활성화된 상태에서 학습 및 테스트 명령어 실행

### 1.3 추가 패키지 설치 (필요 시)

```bash
pip install opencv-python
```

**설명**:
- `opencv-python`: 이미지 합치기 스크립트에 필요
- `environment.yml`에 포함되어 있지만, 설치되지 않은 경우 수동 설치

---

## 2. 합쳐진 이미지 생성

### 2.1 데이터 준비

**폴더 구조**:
```
portrait_retouch/
├── A/                    # 보정 후 이미지들
│   └── train/
│       ├── person001.jpg
│       ├── person002.jpg
│       └── ...
└── B/                    # 보정 전 이미지들 (같은 파일명!)
    └── train/
        ├── person001.jpg    # A/train/person001.jpg와 같은 인물
        ├── person002.jpg
        └── ...
```

**중요 사항**:
- A와 B의 같은 폴더에 있는 이미지는 **반드시 같은 파일명**이어야 함
- 같은 파일명 = 같은 인물의 보정 전/후 쌍
- 이미지 크기는 같을수록 좋음 (다르면 자동 조정됨)

### 2.2 이미지 합치기

```bash
python datasets/combine_A_and_B.py --fold_A ./portrait_retouch/A --fold_B ./portrait_retouch/B --fold_AB ./portrait_retouch
```

**파라미터 설명**:
- `--fold_A`: 보정 후 이미지가 있는 폴더 경로
  - 예: `./portrait_retouch/A`
- `--fold_B`: 보정 전 이미지가 있는 폴더 경로
  - 예: `./portrait_retouch/B`
- `--fold_AB`: 합쳐진 이미지를 저장할 폴더 경로
  - 예: `./portrait_retouch` (결과: `./portrait_retouch/train/`에 저장됨)

**결과**:
- `portrait_retouch/train/` 폴더에 합쳐진 이미지들이 생성됨
- 각 이미지는 왼쪽 절반이 보정 후(A), 오른쪽 절반이 보정 전(B)

**추가 옵션**:
- `--no_multiprocessing`: 멀티프로세싱 비활성화 (Windows에서 문제 발생 시)
  - 예: `python datasets/combine_A_and_B.py --fold_A ./portrait_retouch/A --fold_B ./portrait_retouch/B --fold_AB ./portrait_retouch --no_multiprocessing`

---

## 3. 학습하기

### 3.1 기본 학습 명령어

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 200 --n_epochs_decay 200
```

**파라미터 설명**:
- `--dataroot`: 데이터셋 경로
  - 예: `./portrait_retouch` (train 폴더가 있는 경로)
- `--name`: 실험 이름 (결과 저장 폴더명)
  - 예: `portrait_retouch_reverse`
  - 결과 저장 위치: `./checkpoints/portrait_retouch_reverse/`
- `--model`: 모델 타입
  - 예: `pix2pix` (정렬된 쌍 데이터 사용)
- `--direction`: 변환 방향
  - 예: `AtoB` (보정 후 → 보정 전)
  - 반대: `BtoA` (보정 전 → 보정 후)
- `--batch_size`: 배치 크기
  - 예: `1` (기본값, 메모리에 따라 조정 가능)
- `--load_size`: 이미지 로드 크기
  - 예: `512` (이미지를 512x512로 리사이즈)
- `--crop_size`: 크롭 크기
  - 예: `512` (학습 시 사용할 이미지 크기)
  - `load_size >= crop_size`여야 함
- `--n_epochs`: 학습 에포크 수
  - 예: `200` (초기 학습률로 학습할 에포크 수)
- `--n_epochs_decay`: 학습률 감소 에포크 수
  - 예: `200` (학습률을 0까지 감소시킬 에포크 수)
  - 총 학습 에포크: `n_epochs + n_epochs_decay` = 400 에포크

### 3.2 추가 옵션 포함 학습

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 200 --n_epochs_decay 200 --display_freq 50 --print_freq 10 --save_epoch_freq 10 --use_wandb
```

**추가 파라미터 설명**:
- `--display_freq`: 중간 결과 표시 주기 (iteration)
  - 예: `50` (50 iteration마다 결과 표시)
- `--print_freq`: 손실값 출력 주기 (iteration)
  - 예: `10` (10 iteration마다 손실값 출력)
- `--save_epoch_freq`: 체크포인트 저장 주기 (epoch)
  - 예: `10` (10 epoch마다 모델 저장)
- `--use_wandb`: Weights & Biases 로깅 활성화
  - 선택사항, 학습 진행 상황을 웹 대시보드에서 확인 가능

### 3.3 이어서 학습하기

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --continue_train --epoch latest --epoch_count 201 --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 200 --n_epochs_decay 200
```

**추가 파라미터 설명**:
- `--continue_train`: 이전 학습을 이어서 진행
  - 최신 체크포인트를 자동으로 로드
- `--epoch`: 로드할 체크포인트
  - 예: `latest` (최신 체크포인트)
  - 예: `200` (200번 에포크 체크포인트)
- `--epoch_count`: 시작할 에포크 번호
  - 예: `201` (201번 에포크부터 시작)
  - 마지막 학습 에포크 + 1로 설정

**학습 결과 확인**:
- 모델 저장 위치: `./checkpoints/portrait_retouch_reverse/`
- 중간 결과: `./checkpoints/portrait_retouch_reverse/web/index.html`
- 학습 옵션: `./checkpoints/portrait_retouch_reverse/train_opt.txt`

---

## 4. 학습된 모델 사용

### 4.1 단일 이미지 모드 (보정 후 이미지만 변환)

```bash
python test.py --dataroot ./test_images/test --name portrait_retouch_reverse --model test --direction AtoB --dataset_mode single --epoch latest --netG unet_256 --norm batch
```

**파라미터 설명**:
- `--dataroot`: 테스트 이미지가 있는 폴더 경로
  - 예: `./test_images/test` (보정 후 이미지들이 있는 폴더)
- `--name`: 학습 시 사용한 실험 이름
  - 예: `portrait_retouch_reverse`
- `--model`: 모델 타입
  - 예: `test` (단일 이미지 추론 모드)
- `--direction`: 변환 방향
  - 예: `AtoB` (보정 후 → 보정 전)
- `--dataset_mode`: 데이터셋 모드
  - 예: `single` (단일 이미지 모드, 보정 후 이미지만 필요)
- `--epoch`: 사용할 체크포인트
  - 예: `latest` (최신 체크포인트)
  - 예: `200` (200번 에포크 체크포인트)
- `--netG`: Generator 아키텍처
  - 예: `unet_256` (학습 시 사용한 아키텍처와 동일해야 함)
- `--norm`: Normalization 타입
  - 예: `batch` (학습 시 사용한 타입과 동일해야 함)

**폴더 구조**:
```
test_images/
└── test/
    ├── retouched_photo1.jpg   # 보정 후 이미지만
    ├── retouched_photo2.jpg
    └── ...
```

**결과 위치**:
- `./results/portrait_retouch_reverse/test_latest/index.html` (HTML 결과)
- `./results/portrait_retouch_reverse/test_latest/images/` (이미지 파일)
  - `*_real.png`: 입력 이미지 (보정 후)
  - `*_fake.png`: 생성된 이미지 (보정 전) ✅

### 4.2 고해상도 이미지 변환

```bash
python test.py --dataroot ./test_images/test --name portrait_retouch_reverse --model test --direction AtoB --dataset_mode single --epoch latest --netG unet_256 --norm batch --load_size 512 --crop_size 512 --preprocess resize_and_crop
```

**추가 파라미터 설명**:
- `--load_size`: 이미지 로드 크기
  - 예: `512` (학습 시 사용한 크기와 동일하게 권장)
- `--crop_size`: 크롭 크기
  - 예: `512` (학습 시 사용한 크기와 동일하게 권장)
- `--preprocess`: 전처리 방법
  - 예: `resize_and_crop` (리사이즈 후 크롭)
  - 예: `none` (전처리 없음, 원본 크기 유지)

### 4.3 학습 데이터로 테스트 (합쳐진 이미지 사용)

```bash
python test.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --epoch latest --netG unet_256 --norm batch
```

**파라미터 설명**:
- `--dataroot`: 합쳐진 이미지가 있는 폴더
  - 예: `./portrait_retouch` (train 폴더가 있는 경로)
- `--model`: 모델 타입
  - 예: `pix2pix` (합쳐진 이미지 사용)
- 나머지 파라미터는 위와 동일

**결과**:
- `real_A.png`: 입력 이미지 (보정 후, 합쳐진 이미지의 왼쪽 절반)
- `real_B.png`: 정답 이미지 (보정 전, 합쳐진 이미지의 오른쪽 절반)
- `fake_B.png`: 생성된 이미지 (보정 전)

### 4.4 특정 에포크 모델 사용

```bash
python test.py --dataroot ./test_images/test --name portrait_retouch_reverse --model test --direction AtoB --dataset_mode single --epoch 200 --netG unet_256 --norm batch
```

**파라미터 설명**:
- `--epoch`: 사용할 체크포인트
  - 예: `200` (200번 에포크 모델 사용)
  - 예: `latest` (최신 모델 사용)

---

## 요약

### 전체 워크플로우

1. **환경 구성**: venv 생성 → PyTorch 설치 → 패키지 설치
2. **데이터 준비**: A(보정 후), B(보정 전) 폴더 준비 → 이미지 합치기
3. **학습**: 학습 명령어 실행 → 체크포인트 확인
4. **사용**: 테스트 이미지 준비 → 추론 실행 → 결과 확인

### 빠른 참조

**학습**:
```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 200 --n_epochs_decay 200
```

**테스트**:
```bash
python test.py --dataroot ./test_images/test --name portrait_retouch_reverse --model test --direction AtoB --dataset_mode single --epoch latest --netG unet_256 --norm batch
```

**이어서 학습**:
```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --continue_train --epoch latest --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 200 --n_epochs_decay 200
```

