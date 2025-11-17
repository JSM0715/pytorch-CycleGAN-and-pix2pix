# 종횡비 유지하면서 학습하기

## 문제점

`--preprocess resize_and_crop`을 사용하면:
- 이미지를 정사각형(`load_size x load_size`)으로 리사이즈
- 그 후 `crop_size x crop_size`로 크롭
- **종횡비가 무너짐** (예: 3:4 → 1:1)

## 해결 방법

### 방법 1: `scale_width_and_crop` (권장)

종횡비를 어느 정도 유지하면서 크롭:

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width_and_crop \
    --load_size 1024 \
    --crop_size 1024 \
    --n_epochs 1000 \
    --n_epochs_decay 1000 \
    --lambda_L1 500.0 \
    --lr 0.0001
```

**동작 방식:**
1. 너비를 `load_size`(1024)로 조정하고 종횡비 유지
2. 높이가 1024보다 크면 위/아래를 크롭
3. 높이가 1024보다 작으면 패딩 추가 (또는 리사이즈)

**장점:**
- 종횡비가 어느 정도 유지됨
- 고정 크기 입력으로 배치 처리 가능
- 메모리 효율적

**단점:**
- 여전히 크롭으로 인한 정보 손실 가능

### 방법 2: `scale_width` (완전한 종횡비 유지)

크롭 없이 종횡비 완전 유지:

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width \
    --crop_size 1024 \
    --n_epochs 1000 \
    --n_epochs_decay 1000 \
    --lambda_L1 500.0 \
    --lr 0.0001
```

**동작 방식:**
- 너비를 `crop_size`(1024)로 조정하고 종횡비 유지
- 크롭 없음
- 높이는 종횡비에 따라 자동 결정

**장점:**
- 종횡비 완전 유지
- 정보 손실 없음

**단점:**
- 배치 처리 시 높이가 달라져 문제 발생 가능
- `batch_size 1`로 제한해야 함

### 방법 3: `none` (원본 크기 유지)

원본 크기 그대로 사용:

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --batch_size 1 \
    --preprocess none \
    --n_epochs 1000 \
    --n_epochs_decay 1000 \
    --lambda_L1 500.0 \
    --lr 0.0001
```

**주의사항:**
- 이미지 크기가 **4의 배수**여야 함 (자동 조정됨)
- 메모리 사용량이 매우 큼
- `batch_size 1`로 제한

## 권장 설정

### 현재 설정 개선 (종횡비 유지)

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width_and_crop \
    --load_size 1024 \
    --crop_size 1024 \
    --n_epochs 1000 \
    --n_epochs_decay 1000 \
    --lambda_L1 500.0 \
    --lr 0.0001
```

**변경 사항:**
- `--preprocess resize_and_crop` → `--preprocess scale_width_and_crop`

이렇게 하면:
- 너비를 1024로 조정하고 종횡비 유지
- 높이가 1024보다 크면 위/아래를 크롭
- 종횡비가 어느 정도 유지됨

## 테스트 시 주의사항

학습 시 `scale_width_and_crop`을 사용했다면, 테스트 시에도 동일한 스케일을 유지해야 합니다:

```bash
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --preprocess scale_width \
    --crop_size 1024
```

또는 원본 크기로 테스트:
```bash
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --preprocess none
```

## 비교표

| 옵션 | 종횡비 유지 | 크롭 | 배치 처리 | 메모리 |
|------|------------|------|----------|--------|
| `resize_and_crop` | ❌ | ✅ | ✅ | 효율적 |
| `scale_width_and_crop` | ⚠️ (부분) | ✅ | ✅ | 효율적 |
| `scale_width` | ✅ | ❌ | ⚠️ (제한적) | 보통 |
| `none` | ✅ | ❌ | ❌ | 비효율적 |

