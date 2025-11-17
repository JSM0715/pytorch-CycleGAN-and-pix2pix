# 데이터 준비 가이드

이 문서는 CycleGAN과 pix2pix 모델 학습을 위한 데이터 준비 방법을 설명합니다.

## 📁 CycleGAN 데이터 준비 (비정렬 데이터)

CycleGAN은 **정렬되지 않은(unpaired)** 데이터를 사용합니다. 즉, 도메인 A와 도메인 B의 이미지가 서로 대응되지 않아도 됩니다.

### 폴더 구조

```
your_dataset/
├── trainA/          # 도메인 A의 학습 이미지들
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── trainB/          # 도메인 B의 학습 이미지들
│   ├── img1.jpg
│   ├── img2.jpg
│   └── ...
├── testA/           # (선택사항) 도메인 A의 테스트 이미지들
│   └── ...
└── testB/           # (선택사항) 도메인 B의 테스트 이미지들
    └── ...
```

### 예시: 말 → 얼룩말 변환

```
datasets/
└── horse2zebra/
    ├── trainA/      # 말 이미지들
    │   ├── horse001.jpg
    │   ├── horse002.jpg
    │   └── ...
    ├── trainB/      # 얼룩말 이미지들
    │   ├── zebra001.jpg
    │   ├── zebra002.jpg
    │   └── ...
    ├── testA/       # 테스트용 말 이미지들
    └── testB/       # 테스트용 얼룩말 이미지들
```

### 학습 명령어

```bash
python train.py --dataroot ./datasets/your_dataset --name your_experiment --model cycle_gan
```

### 주의사항

- **이미지 개수**: trainA와 trainB의 이미지 개수가 달라도 됩니다
- **파일명**: 파일명이 일치할 필요가 없습니다
- **이미지 크기**: 자동으로 리사이즈되지만, 너무 작거나 큰 이미지는 성능에 영향을 줄 수 있습니다
- **데이터 품질**: 두 도메인이 시각적으로 유사한 내용을 공유할수록 좋습니다 (예: 말↔얼룩말은 좋지만, 고양이↔키보드는 작동하지 않을 수 있음)

---

## 📁 pix2pix 데이터 준비 (정렬 데이터)

pix2pix는 **정렬된(paired)** 데이터를 사용합니다. 즉, 도메인 A와 도메인 B의 이미지가 서로 대응되어야 합니다.

### 방법 1: A, B 폴더를 분리하여 준비 후 합치기

#### 1단계: 초기 폴더 구조 준비

```
your_data/
├── A/               # 도메인 A 이미지들
│   ├── train/
│   │   ├── 001.jpg
│   │   ├── 002.jpg
│   │   └── ...
│   ├── val/         # (선택사항)
│   └── test/        # (선택사항)
└── B/               # 도메인 B 이미지들 (A와 대응)
    ├── train/
    │   ├── 001.jpg   # A/train/001.jpg와 대응
    │   ├── 002.jpg   # A/train/002.jpg와 대응
    │   └── ...
    ├── val/
    └── test/
```

**중요**: 
- A와 B의 같은 폴더(train, val, test)에 있는 이미지들은 **같은 파일명**을 가져야 합니다
- **같은 크기**여야 합니다

#### 2단계: 이미지 합치기

```bash
python datasets/combine_A_and_B.py --fold_A /path/to/your_data/A --fold_B /path/to/your_data/B --fold_AB /path/to/your_data
```

이 명령어는 A와 B 이미지를 좌우로 합쳐서 하나의 이미지로 만듭니다.

#### 3단계: 최종 폴더 구조

```
your_data/
├── train/           # 합쳐진 이미지들 (A|B 형태)
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
├── val/             # (선택사항)
└── test/            # (선택사항)
```

### 방법 2: 이미 합쳐진 이미지 사용

이미 A와 B가 좌우로 합쳐진 이미지가 있다면, 그대로 사용할 수 있습니다.

```
your_data/
├── train/
│   ├── img001.jpg   # 왼쪽 절반이 A, 오른쪽 절반이 B
│   ├── img002.jpg
│   └── ...
└── test/
    └── ...
```

### 예시: 레이블 맵 → 사진 변환

```
datasets/
└── facades/
    ├── train/
    │   ├── 001.jpg   # 왼쪽: 레이블 맵, 오른쪽: 실제 사진
    │   ├── 002.jpg
    │   └── ...
    └── test/
        └── ...
```

### 학습 명령어

```bash
python train.py --dataroot ./datasets/your_data --name your_experiment --model pix2pix --direction AtoB
```

또는

```bash
python train.py --dataroot ./datasets/your_data --name your_experiment --model pix2pix --direction BtoA
```

---

## 🖼️ 이미지 형식 요구사항

- **지원 형식**: JPG, PNG 등 PIL/Pillow가 지원하는 모든 형식
- **권장 크기**: 
  - 최소: 256x256 픽셀
  - 권장: 512x512 이상
  - 큰 이미지: 1024x1024도 가능하지만 메모리 사용량이 증가합니다
- **색상**: RGB 또는 Grayscale 모두 지원
- **비율**: 정사각형이 아니어도 되지만, `--preprocess` 옵션에 따라 처리됩니다

---

## 📝 실제 예시: 자체 데이터셋 준비

### 예시 1: 스케치 → 컬러 이미지 (pix2pix)

```
my_sketch2color/
├── A/
│   └── train/
│       ├── sketch_001.jpg
│       ├── sketch_002.jpg
│       └── ...
└── B/
    └── train/
        ├── sketch_001.jpg    # 같은 파일명, 컬러 버전
        ├── sketch_002.jpg
        └── ...

# 합치기
python datasets/combine_A_and_B.py --fold_A ./my_sketch2color/A --fold_B ./my_sketch2color/B --fold_AB ./my_sketch2color

# 학습
python train.py --dataroot ./my_sketch2color --name sketch2color --model pix2pix --direction AtoB
```

### 예시 2: 낮 → 밤 변환 (CycleGAN)

```
my_day2night/
├── trainA/          # 낮 사진들
│   ├── day001.jpg
│   ├── day002.jpg
│   └── ...
└── trainB/          # 밤 사진들
    ├── night001.jpg
    ├── night002.jpg
    └── ...

# 학습
python train.py --dataroot ./my_day2night --name day2night --model cycle_gan
```

---

## 🔍 데이터 검증

데이터를 준비한 후, 다음 명령어로 확인할 수 있습니다:

```python
# Python에서 간단히 확인
import os
from pathlib import Path

# CycleGAN 데이터 확인
dataroot = "./datasets/your_dataset"
trainA = Path(dataroot) / "trainA"
trainB = Path(dataroot) / "trainB"

print(f"trainA 이미지 개수: {len(list(trainA.glob('*.jpg')))}")
print(f"trainB 이미지 개수: {len(list(trainB.glob('*.jpg')))}")

# pix2pix 데이터 확인
train = Path(dataroot) / "train"
print(f"train 이미지 개수: {len(list(train.glob('*.jpg')))}")
```

---

## ⚠️ 주의사항

1. **데이터 양**: 최소 수백 장 이상의 이미지가 필요합니다. 더 많을수록 좋습니다.
2. **데이터 품질**: 
   - CycleGAN: 두 도메인이 시각적으로 유사한 내용을 공유해야 합니다
   - pix2pix: 정확히 대응되는 쌍이 필요합니다
3. **이미지 크기**: 
   - 너무 작으면 (64x64 이하) 품질이 떨어질 수 있습니다
   - 너무 크면 (2048x2048 이상) 메모리 부족이 발생할 수 있습니다
4. **메모리**: 
   - CycleGAN은 4개의 네트워크를 사용하므로 메모리를 많이 사용합니다
   - 큰 이미지는 `--crop_size`를 사용하여 크롭하세요

---

## 📚 추가 리소스

- 공식 데이터셋 다운로드:
  - CycleGAN: `bash ./datasets/download_cyclegan_dataset.sh dataset_name`
  - pix2pix: `bash ./datasets/download_pix2pix_dataset.sh dataset_name`
- 자세한 정보: `docs/datasets.md` 참고

