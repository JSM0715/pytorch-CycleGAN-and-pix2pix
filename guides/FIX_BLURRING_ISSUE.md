# 보정 영역 주변 흐림 문제 해결 가이드

## 문제 분석

픽셀 유동화로 보정된 이미지(턱선 축소, 안면 길이 보정)를 원본으로 복원할 때, **보정된 영역 주변의 이미지가 흐려지는** 문제가 발생합니다.

### 원인

1. **L1 Loss의 평균화 효과**
   - L1 loss는 픽셀 단위 평균 제곱 오차를 최소화
   - 여러 가능한 해석 중 평균값을 선택하는 경향
   - 결과적으로 **흐린(blurred) 이미지** 생성

2. **주변 픽셀 정보 부족**
   - 보정된 영역 주변의 픽셀 정보가 손실됨
   - 모델이 주변 영역을 복구할 충분한 정보를 학습하지 못함

3. **Discriminator의 한계**
   - Discriminator가 흐린 이미지와 선명한 이미지를 구분하지 못함
   - Generator가 흐린 결과를 생성해도 패널티가 적음

## 해결 방법

### 방법 1: Perceptual Loss 추가 (권장) ⭐

**Perceptual Loss**는 픽셀 단위가 아닌 **고수준 feature**를 비교하여 선명도를 향상시킵니다.

#### 구현 방법

1. **새 모델 파일 생성**: `models/pix2pix_model_with_perceptual.py` (이미 생성됨)

2. **모델 등록**: `models/__init__.py`에 추가

3. **학습 명령어**:
```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix_with_perceptual \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width_and_crop \
    --load_size 1024 \
    --crop_size 1024 \
    --n_epochs 1000 \
    --n_epochs_decay 1000 \
    --lambda_L1 100.0 \
    --lambda_perceptual 10.0 \
    --use_perceptual \
    --lr 0.0001
```

**하이퍼파라미터 조정**:
- `--lambda_perceptual 10.0`: Perceptual loss 가중치 (5.0 ~ 20.0 권장)
  - 너무 크면: 색상 왜곡 가능
  - 너무 작으면: 효과 미미
- `--lambda_L1 100.0`: L1 loss 가중치 (기존 유지 또는 약간 감소)

### 방법 2: L1 Loss 가중치 조정

L1 loss를 줄이고 GAN loss를 강화:

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
    --lambda_L1 50.0 \
    --lr 0.0001
```

**변경 사항**:
- `--lambda_L1 500.0` → `--lambda_L1 50.0` (L1 loss 감소)
- GAN loss가 상대적으로 강해져 선명도 향상

### 방법 3: Discriminator 강화

더 강한 Discriminator로 선명도 향상:

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
    --lambda_L1 100.0 \
    --netD basic \
    --n_layers_D 4 \
    --lr 0.0001
```

**변경 사항**:
- `--n_layers_D 4`: Discriminator 레이어 수 증가 (기본값: 3)
- 더 강한 판별력으로 선명한 이미지 생성 유도

### 방법 4: GAN Mode 변경

LSGAN으로 변경하여 학습 안정성 향상:

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
    --lambda_L1 100.0 \
    --gan_mode lsgan \
    --lr 0.0001
```

**변경 사항**:
- `--gan_mode vanilla` → `--gan_mode lsgan`
- LSGAN은 더 안정적인 학습과 선명한 결과 생성

### 방법 5: 학습 전략 조정

#### Progressive Training
작은 크기로 시작하여 점진적으로 크기 증가:

```bash
# 1단계: 256x256으로 학습
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse_stage1 \
    --model pix2pix \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width_and_crop \
    --load_size 512 \
    --crop_size 256 \
    --n_epochs 500 \
    --n_epochs_decay 500 \
    --lambda_L1 100.0 \
    --lr 0.0002

# 2단계: 1024x1024로 fine-tuning
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width_and_crop \
    --load_size 1024 \
    --crop_size 1024 \
    --n_epochs 500 \
    --n_epochs_decay 500 \
    --lambda_L1 100.0 \
    --lr 0.0001 \
    --continue_train \
    --epoch_count 501 \
    --load_pretrain ./checkpoints/portrait_retouch_reverse_stage1
```

## 권장 조합

### 최적 설정 (Perceptual Loss 사용)

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix_with_perceptual \
    --direction AtoB \
    --batch_size 1 \
    --preprocess scale_width_and_crop \
    --load_size 1024 \
    --crop_size 1024 \
    --n_epochs 1000 \
    --n_epochs_decay 1000 \
    --lambda_L1 100.0 \
    --lambda_perceptual 10.0 \
    --use_perceptual \
    --gan_mode lsgan \
    --lr 0.0001
```

### 대안 설정 (Perceptual Loss 없이)

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
    --lambda_L1 50.0 \
    --gan_mode lsgan \
    --n_layers_D 4 \
    --lr 0.0001
```

## 하이퍼파라미터 튜닝 가이드

### lambda_L1 조정
- **높은 값 (200-500)**: 픽셀 정확도 높음, 하지만 흐림 가능
- **중간 값 (50-100)**: 균형잡힌 결과
- **낮은 값 (10-50)**: 선명도 향상, 하지만 색상 왜곡 가능

### lambda_perceptual 조정
- **5.0-10.0**: 보수적, 안정적
- **10.0-20.0**: 권장 범위
- **20.0 이상**: 색상 왜곡 위험

### 학습률 조정
- **0.0002**: 빠른 학습, 불안정 가능
- **0.0001**: 권장 (안정적)
- **0.00005**: 느린 학습, 더 안정적

## 모니터링

학습 중 다음을 확인하세요:

1. **Loss 값**:
   - `G_L1`: 점진적으로 감소해야 함
   - `G_Perceptual`: 점진적으로 감소해야 함
   - `G_GAN`: 안정적으로 유지

2. **생성된 이미지**:
   - `checkpoints/portrait_retouch_reverse/web/index.html` 확인
   - 보정 영역 주변의 선명도 개선 여부 확인

3. **과적합 방지**:
   - 학습 데이터가 적으면 validation set으로 확인
   - Loss가 더 이상 감소하지 않으면 조기 종료 고려

## 추가 팁

1. **데이터 품질**: 고품질 원본-보정 쌍 사용
2. **데이터 증강**: `--no_flip False`로 수평 플립 활성화
3. **정기적 체크포인트**: 중간 결과 확인 및 조정
4. **Fine-tuning**: 기존 모델에서 시작하여 빠른 수렴

