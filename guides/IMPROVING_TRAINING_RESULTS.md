# 학습 결과 개선 가이드

## 🔍 현재 문제 분석

### 문제점
1. **예측 결과가 크게 변화 없음**: 모델이 입력과 유사한 결과만 생성
2. **얼굴 질감이 보정 전으로 잘 안 돌아감**: 세부 질감 복원 실패
3. **데이터 부족**: 현재 3개만 있음 (매우 부족)

### 원인 분석

#### 1. 데이터 부족 (가장 큰 문제)
- **현재**: 3개 이미지
- **권장**: 최소 500-1000 쌍 이상
- **영향**: 
  - 과적합 (overfitting) 발생
  - 일반화 성능 저하
  - 다양한 얼굴/조명/각도 학습 불가

#### 2. 학습 횟수
- 현재: 400 에포크 (200 + 200)
- 데이터가 적으면 더 많은 에포크가 필요할 수 있음
- 하지만 데이터가 너무 적으면 과적합만 심해질 수 있음

#### 3. 하이퍼파라미터
- `lambda_L1`: 100.0 (L1 loss 가중치)
- `lr`: 0.0002 (학습률)
- `batch_size`: 1

## 💡 해결 방법

### 방법 1: 데이터 증강 (Data Augmentation) - 즉시 적용 가능

데이터가 적을 때 가장 효과적인 방법입니다.

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 1024 --crop_size 1024 --n_epochs 200 --n_epochs_decay 200 --preprocess resize_and_crop --no_flip False
```

**주요 변경사항**:
- `--no_flip False`: 이미지 플립 활성화 (데이터 증강)
  - 기본값이 False이므로 명시적으로 설정
  - 수평 플립으로 데이터 2배 증가 효과

**추가 데이터 증강 옵션**:
- `--preprocess resize_and_crop`: 랜덤 크롭으로 다양한 영역 학습
- 이미지 회전, 색상 조정 등은 코드 수정 필요

### 방법 2: L1 Loss 가중치 조정

얼굴 질감 복원을 위해 L1 loss를 강화할 수 있습니다.

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 1024 --crop_size 1024 --n_epochs 200 --n_epochs_decay 200 --lambda_L1 200.0
```

**파라미터 설명**:
- `--lambda_L1`: L1 loss 가중치
  - 기본값: `100.0`
  - 증가 예: `200.0`, `300.0` (더 강한 픽셀 단위 정확도)
  - 감소 예: `50.0` (더 자유로운 변환 허용)

**효과**:
- 높은 값: 더 정확한 픽셀 매칭, 질감 복원 강화
- 낮은 값: 더 창의적인 변환, 하지만 정확도 감소

### 방법 3: 학습률 조정

더 세밀한 학습을 위해 학습률을 낮출 수 있습니다.

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 1024 --crop_size 1024 --n_epochs 200 --n_epochs_decay 200 --lr 0.0001
```

**파라미터 설명**:
- `--lr`: 학습률
  - 기본값: `0.0002`
  - 낮춤 예: `0.0001` (더 안정적인 학습)
  - 높임 예: `0.0005` (더 빠른 학습, 불안정할 수 있음)

### 방법 4: 더 많은 에포크 학습

데이터가 적을 때 더 오래 학습할 수 있습니다.

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 1024 --crop_size 1024 --n_epochs 400 --n_epochs_decay 400 --continue_train
```

**파라미터 설명**:
- `--n_epochs`: 초기 학습 에포크
  - 예: `400` (기존 200에서 증가)
- `--n_epochs_decay`: 학습률 감소 에포크
  - 예: `400` (기존 200에서 증가)
- `--continue_train`: 기존 모델에서 이어서 학습

**주의**: 데이터가 너무 적으면 과적합만 심해질 수 있음

### 방법 5: 이미지 크기 조정

더 작은 크기로 학습하여 더 많은 iteration을 수행할 수 있습니다.

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 400 --n_epochs_decay 400 --continue_train
```

**파라미터 설명**:
- `--load_size`: 이미지 로드 크기
  - 예: `512` (기존 1024에서 감소)
- `--crop_size`: 크롭 크기
  - 예: `512` (기존 1024에서 감소)

**효과**:
- 더 빠른 학습 (작은 이미지)
- 더 많은 iteration 가능
- 메모리 사용량 감소

### 방법 6: Generator 아키텍처 변경

더 강력한 Generator를 사용할 수 있습니다.

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse_v2 --model pix2pix --direction AtoB --batch_size 1 --load_size 1024 --crop_size 1024 --n_epochs 200 --n_epochs_decay 200 --netG resnet_9blocks
```

**파라미터 설명**:
- `--netG`: Generator 아키텍처
  - 기본값: `unet_256`
  - 변경 예: `resnet_9blocks` (더 깊은 네트워크, 더 복잡한 변환 학습 가능)
  - 다른 옵션: `resnet_6blocks`, `unet_128`

**주의**: 아키텍처 변경 시 기존 모델과 호환되지 않음 (새로 학습 필요)

## 🎯 권장 조합

### 즉시 시도 가능한 조합 1: 데이터 증강 + L1 강화

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 1024 --crop_size 1024 --n_epochs 400 --n_epochs_decay 400 --lambda_L1 200.0 --continue_train
```

### 즉시 시도 가능한 조합 2: 작은 크기 + 더 많은 에포크

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 600 --n_epochs_decay 600 --lambda_L1 150.0 --continue_train
```

## 📊 데이터 부족 문제 해결

### 근본적인 해결책: 더 많은 데이터 수집

**최소 권장량**:
- **절대 최소**: 100-200 쌍
- **권장**: 500-1000 쌍
- **이상적**: 1000+ 쌍

**데이터 품질**:
- 다양한 얼굴 (성별, 나이, 인종 등)
- 다양한 조명 조건
- 다양한 각도 (정면, 측면 등)
- 다양한 보정 스타일 (일관성 있게)

### 데이터 증강 활용

데이터가 적을 때는 증강이 필수입니다:
- 이미지 플립 (`--no_flip False`)
- 랜덤 크롭 (`--preprocess resize_and_crop`)
- 추가 증강은 코드 수정 필요 (회전, 색상 조정 등)

## 🔬 실험적 접근

### 실험 1: L1 Loss 가중치 실험

```bash
# 실험 1: 기본값
python train.py ... --lambda_L1 100.0 --name exp_l1_100

# 실험 2: 증가
python train.py ... --lambda_L1 200.0 --name exp_l1_200

# 실험 3: 더 증가
python train.py ... --lambda_L1 300.0 --name exp_l1_300
```

각 실험 결과를 비교하여 최적값 찾기

### 실험 2: 학습률 실험

```bash
# 실험 1: 기본값
python train.py ... --lr 0.0002 --name exp_lr_0002

# 실험 2: 감소
python train.py ... --lr 0.0001 --name exp_lr_0001

# 실험 3: 더 감소
python train.py ... --lr 0.00005 --name exp_lr_00005
```

## ⚠️ 주의사항

### 과적합 (Overfitting)

데이터가 적을 때 주의할 점:
- 학습 데이터에서는 잘 작동하지만 새로운 이미지에서는 성능 저하
- 해결: 더 많은 데이터, 데이터 증강, 정규화 강화

### 학습 시간

더 많은 에포크는 더 긴 학습 시간을 의미합니다:
- 400 에포크: 기존의 2배 시간
- 600 에포크: 기존의 3배 시간

## 📈 모니터링

### 학습 진행 확인

```bash
# HTML 결과 확인
# ./checkpoints/portrait_retouch_reverse/web/index.html

# 손실 로그 확인
# ./checkpoints/portrait_retouch_reverse/loss_log.txt
```

### 평가 방법

1. **시각적 평가**: 중간 결과 이미지 확인
2. **손실값**: 하지만 GAN에서는 손실값이 성능을 완전히 반영하지 않음
3. **실제 테스트**: 새로운 이미지로 테스트하여 일반화 성능 확인

## 💡 종합 권장사항

### 단기 해결책 (데이터 부족 상황)

1. **데이터 증강 활성화**: `--no_flip False` (이미 기본값)
2. **L1 Loss 강화**: `--lambda_L1 200.0` 또는 `300.0`
3. **더 많은 에포크**: `--n_epochs 400 --n_epochs_decay 400`
4. **작은 이미지로 시작**: `--load_size 512 --crop_size 512`

### 장기 해결책

1. **더 많은 데이터 수집**: 최소 100-200 쌍 이상
2. **데이터 품질 향상**: 다양한 조건의 이미지
3. **전이 학습**: 사전 학습된 모델 활용 (가능한 경우)

## 🎯 최종 권장 명령어

### 현재 상황에 최적화된 명령어

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 600 --n_epochs_decay 600 --lambda_L1 200.0 --continue_train
```

**이유**:
- 작은 이미지로 더 많은 iteration 가능
- L1 loss 강화로 질감 복원 개선
- 더 많은 에포크로 충분한 학습
- 기존 모델에서 이어서 학습

