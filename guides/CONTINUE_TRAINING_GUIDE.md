# 이어서 학습하기 (Resume Training)

학습을 중단했거나 추가로 더 학습하고 싶을 때 사용하는 방법입니다.

## 기본 방법

### 방법 1: 최신 체크포인트에서 이어서 학습

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --continue_train \
    --batch_size 1 \
    --load_size 512 \
    --crop_size 512 \
    --n_epochs 200 \
    --n_epochs_decay 200
```

**설명**:
- `--continue_train`: 이전 학습을 이어서 진행
- `--epoch latest`: 최신 체크포인트를 자동으로 로드 (기본값)

### 방법 2: 특정 에포크에서 이어서 학습

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --continue_train \
    --epoch 200 \
    --epoch_count 201 \
    --batch_size 1 \
    --load_size 512 \
    --crop_size 512 \
    --n_epochs 200 \
    --n_epochs_decay 200
```

**설명**:
- `--epoch 200`: 200번 에포크의 체크포인트를 로드
- `--epoch_count 201`: 201번 에포크부터 시작

## 주요 옵션

### `--continue_train`
- 이전 학습을 이어서 진행하는 플래그
- 최신 체크포인트(`latest_net_G.pth`, `latest_net_D.pth`)를 자동으로 로드

### `--epoch`
- 로드할 체크포인트 지정
- `latest`: 최신 체크포인트 (기본값)
- `200`: 200번 에포크의 체크포인트

### `--epoch_count`
- 학습을 시작할 에포크 번호
- 기본값: 1
- 예: 200번 에포크까지 학습했다면 `--epoch_count 201`로 설정

## 실제 사용 예시

### 예시 1: 최신 모델에서 이어서 학습

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --continue_train \
    --batch_size 1 \
    --load_size 512 \
    --crop_size 512 \
    --n_epochs 200 \
    --n_epochs_decay 200 \
    --display_freq 50 \
    --print_freq 10 \
    --save_epoch_freq 10
```

### 예시 2: 특정 에포크에서 이어서 추가 학습

200번 에포크까지 학습했고, 100번 에포크 더 학습하고 싶다면:

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --continue_train \
    --epoch 200 \
    --epoch_count 201 \
    --batch_size 1 \
    --load_size 512 \
    --crop_size 512 \
    --n_epochs 100 \
    --n_epochs_decay 100
```

이렇게 하면 201번 에포크부터 300번 에포크까지 학습합니다.

## 주의사항

### 1. 학습 옵션 일치

이어서 학습할 때는 **원래 학습 시 사용한 옵션과 동일**하게 설정해야 합니다:
- `--netG unet_256`
- `--norm batch`
- `--no_dropout` 플래그 사용 여부
- `--load_size`, `--crop_size`
- 기타 네트워크 아키텍처 관련 옵션

### 2. 에포크 카운트

- `--epoch_count`를 올바르게 설정하지 않으면 에포크 번호가 겹칠 수 있습니다
- 예: 200번까지 학습했다면 `--epoch_count 201`로 설정

### 3. 체크포인트 확인

이어서 학습하기 전에 체크포인트가 있는지 확인:

```bash
# Windows
dir checkpoints\portrait_retouch_reverse\*.pth

# Linux/macOS
ls checkpoints/portrait_retouch_reverse/*.pth
```

## 학습 옵션 확인

원래 학습 시 사용한 옵션을 확인하려면:

```bash
# Windows
type checkpoints\portrait_retouch_reverse\train_opt.txt

# Linux/macOS
cat checkpoints/portrait_retouch_reverse/train_opt.txt
```

## 빠른 참조

### 가장 간단한 명령어

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --continue_train
```

### 한 줄 명령어 (전체 옵션 포함)

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB --continue_train --batch_size 1 --load_size 512 --crop_size 512 --n_epochs 200 --n_epochs_decay 200 --display_freq 50 --print_freq 10 --save_epoch_freq 10
```

## 문제 해결

### 체크포인트를 찾을 수 없는 경우

- `--continue_train`을 사용해도 체크포인트가 없으면 처음부터 학습을 시작합니다
- 경고 메시지가 출력됩니다: "Warning: Checkpoint ... not found. Starting training from scratch."

### 학습이 중단된 경우

- 학습이 중단되어도 `latest_net_G.pth`와 `latest_net_D.pth`가 저장되어 있다면 이어서 학습할 수 있습니다
- `--save_latest_freq` 옵션에 따라 주기적으로 최신 모델이 저장됩니다 (기본값: 5000 iteration)

