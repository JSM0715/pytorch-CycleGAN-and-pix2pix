# 전처리 옵션 가이드

## 전처리 옵션 종류

학습 시 사용할 수 있는 전처리 옵션들:

### 1. `resize_and_crop` (기본값, 권장)
```bash
--preprocess resize_and_crop --load_size 1024 --crop_size 1024
```
- **동작**: 이미지를 `load_size`로 리사이즈한 후, `crop_size`로 랜덤 크롭
- **장점**: 
  - 다양한 영역을 학습할 수 있어 일반화 성능 향상
  - 메모리 효율적 (고정 크기)
- **단점**: 원본 비율이 무시될 수 있음

### 2. `crop`
```bash
--preprocess crop --crop_size 512
```
- **동작**: 리사이즈 없이 원본 이미지에서 `crop_size`로 랜덤 크롭
- **장점**: 원본 해상도 유지
- **단점**: 
  - 이미지가 `crop_size`보다 작으면 오류 발생
  - 배치 처리 시 크기 불일치 문제

### 3. `scale_width`
```bash
--preprocess scale_width --crop_size 512
```
- **동작**: 너비를 `crop_size`로 조정하고 비율 유지
- **장점**: 종횡비 유지
- **단점**: 높이가 다양해져 배치 처리 어려움

### 4. `scale_width_and_crop`
```bash
--preprocess scale_width_and_crop --load_size 1024 --crop_size 512
```
- **동작**: 너비를 `load_size`로 조정한 후, `crop_size`로 랜덤 크롭
- **장점**: 종횡비를 어느 정도 유지하면서 크롭 가능
- **단점**: 여전히 크롭으로 인한 정보 손실

### 5. `none` (전처리 최소화)
```bash
--preprocess none
```
- **동작**: 리사이즈/크롭 없이 원본 크기 유지
- **주의사항**: 
  - 이미지 크기가 **4의 배수**여야 함 (Generator 다운샘플링 때문)
  - 자동으로 4의 배수로 조정됨 (`__make_power_2` 함수)
  - 메모리 사용량이 매우 큼 (큰 이미지의 경우)
- **장점**: 원본 해상도 완전 보존
- **단점**: 
  - 메모리 부족 가능성
  - 배치 크기를 1로 제한해야 할 수 있음

## 리사이즈/크롭이 필수인가?

### 답: **필수는 아니지만 권장됩니다**

**이유:**

1. **Generator 아키텍처 제약**
   - Generator는 다운샘플링/업샘플링을 수행
   - 입력 크기가 4의 배수가 아니면 출력 크기가 달라질 수 있음
   - `preprocess none`을 사용해도 자동으로 4의 배수로 조정됨

2. **메모리 효율성**
   - 고정 크기 입력으로 배치 처리 가능
   - GPU 메모리 사용량 예측 가능

3. **학습 안정성**
   - 다양한 크기의 이미지가 섞이면 배치 처리 어려움
   - `crop` 옵션은 이미지가 `crop_size`보다 작으면 오류 발생

## 권장 설정

### 고해상도 학습 (권장)
```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --preprocess resize_and_crop \
    --load_size 1024 \
    --crop_size 1024 \
    --batch_size 1
```

### 원본 해상도 유지 (메모리 여유 시)
```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --preprocess none \
    --batch_size 1
```
**주의**: 모든 이미지가 4의 배수 크기여야 함

### 종횡비 유지하면서 학습
```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --preprocess scale_width_and_crop \
    --load_size 1024 \
    --crop_size 512 \
    --batch_size 1
```

## 테스트 시 전처리

테스트 시에는 학습과 동일한 전처리를 사용하는 것이 좋습니다:

```bash
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --preprocess resize_and_crop \
    --load_size 1024 \
    --crop_size 1024
```

또는 원본 크기 유지:
```bash
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --preprocess none
```

## 요약

- **리사이즈/크롭은 필수는 아님** (`preprocess none` 사용 가능)
- 하지만 **권장됨** (메모리 효율, 학습 안정성)
- `preprocess none` 사용 시 이미지 크기는 **4의 배수**여야 함
- 대부분의 경우 `resize_and_crop`이 가장 안정적

