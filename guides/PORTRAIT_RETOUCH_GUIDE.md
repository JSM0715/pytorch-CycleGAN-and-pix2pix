# 인물 보정 후 → 보정 전 변환 가이드

인물 보정 후 사진을 보정 전 사진으로 되돌리는 학습을 위한 데이터 준비 및 학습 방법입니다.

## ✅ 모델 선택: pix2pix 사용

**중요**: 같은 인물의 보정 전/후 쌍이 필요하므로 **pix2pix (paired data)**를 사용해야 합니다.
- ✅ **pix2pix**: 정렬된 쌍 데이터 필요 (보정 후 → 보정 전)
- ❌ **CycleGAN**: 정렬되지 않은 데이터 사용 (적합하지 않음)

## 📁 데이터 준비 방법

### 방법 1: A, B 폴더 분리 후 합치기 (권장)

#### 1단계: 폴더 구조 준비

```
portrait_retouch/
├── A/                    # 보정 후 이미지들 (입력)
│   └── train/
│       ├── person001_retouched.jpg
│       ├── person002_retouched.jpg
│       ├── person003_retouched.jpg
│       └── ...
└── B/                    # 보정 전 이미지들 (출력, 같은 파일명!)
    └── train/
        ├── person001_retouched.jpg    # A/train/person001_retouched.jpg와 같은 인물
        ├── person002_retouched.jpg    # A/train/person002_retouched.jpg와 같은 인물
        ├── person003_retouched.jpg
        └── ...
```

**핵심 요구사항**:
- ✅ **같은 파일명**: A와 B의 같은 폴더에 있는 이미지는 **반드시 같은 파일명**이어야 합니다
- ✅ **같은 인물**: 같은 파일명의 이미지는 **같은 인물**의 보정 전/후 사진이어야 합니다
- ✅ **같은 크기**: 두 이미지의 크기가 같아야 합니다 (다르면 자동으로 조정되지만, 원본 크기가 같으면 좋습니다)

#### 2단계: 이미지 합치기

```bash
python datasets/combine_A_and_B.py --fold_A ./portrait_retouch/A --fold_B ./portrait_retouch/B --fold_AB ./portrait_retouch
```

이 명령어는:
- A/train/person001_retouched.jpg (보정 후)와 B/train/person001_retouched.jpg (보정 전)를
- 좌우로 합쳐서 portrait_retouch/train/person001_retouched.jpg로 저장합니다
- 왼쪽 절반: 보정 후, 오른쪽 절반: 보정 전

#### 3단계: 최종 폴더 구조 확인

```
portrait_retouch/
└── train/                # 합쳐진 이미지들
    ├── person001_retouched.jpg   # 왼쪽: 보정 후, 오른쪽: 보정 전
    ├── person002_retouched.jpg
    └── ...
```

### 방법 2: 이미 합쳐진 이미지 사용

이미 보정 전/후가 좌우로 합쳐진 이미지가 있다면 그대로 사용할 수 있습니다:

```
portrait_retouch/
└── train/
    ├── pair001.jpg   # 왼쪽: 보정 후, 오른쪽: 보정 전
    ├── pair002.jpg
    └── ...
```

## 🚀 학습 명령어

### 기본 학습

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --use_wandb
```

**설명**:
- `--dataroot`: 데이터셋 경로
- `--name`: 실험 이름 (결과 저장 폴더명)
- `--model pix2pix`: pix2pix 모델 사용
- `--direction AtoB`: A(보정 후) → B(보정 전) 방향으로 학습
- `--use_wandb`: (선택사항) Weights & Biases 로깅

### 추가 옵션

```bash
python train.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --batch_size 4 \
    --load_size 512 \
    --crop_size 512 \
    --n_epochs 200 \
    --n_epochs_decay 200 \
    --use_wandb
```

**옵션 설명**:
- `--batch_size`: 배치 크기 (메모리에 따라 조정, 기본값: 1)
- `--load_size`: 이미지 로드 크기 (기본값: 286)
- `--crop_size`: 크롭 크기 (기본값: 256, 512로 설정하면 더 고해상도)
- `--n_epochs`: 학습 에포크 수
- `--n_epochs_decay`: 학습률 감소 에포크 수

## 🧪 테스트

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch latest
```

결과는 `./results/portrait_retouch_reverse/test_latest/index.html`에 저장됩니다.

## 📝 데이터 준비 체크리스트

### 필수 사항
- [ ] 같은 인물의 보정 전/후 쌍이 준비되어 있음
- [ ] A와 B 폴더의 같은 파일명이 같은 인물을 나타냄
- [ ] 이미지 크기가 적절함 (최소 256x256, 권장 512x512 이상)
- [ ] 충분한 데이터량 (최소 수백 장, 많을수록 좋음)

### 권장 사항
- [ ] 다양한 조명 조건의 이미지 포함
- [ ] 다양한 각도의 얼굴 포함
- [ ] 다양한 보정 스타일 포함 (일관성 있게)
- [ ] 테스트용 데이터셋도 준비 (test 폴더)

## 💡 팁

### 1. 데이터 품질
- 보정 전/후가 **같은 인물, 같은 포즈, 같은 조명**이어야 학습이 잘 됩니다
- 배경이 크게 달라지지 않도록 주의하세요

### 2. 이미지 크기
- 인물 사진의 경우 **512x512 이상**을 권장합니다
- 더 큰 이미지(1024x1024)도 가능하지만 메모리 사용량이 증가합니다

### 3. 데이터 양
- 최소 **500-1000 쌍** 이상 권장
- 더 많을수록 일반화 성능이 좋아집니다

### 4. 학습 모니터링
- `--use_wandb` 옵션으로 학습 진행 상황을 실시간으로 확인할 수 있습니다
- 또는 `./checkpoints/portrait_retouch_reverse/web/index.html`에서 확인

## 🔍 데이터 검증 스크립트

데이터를 준비한 후 다음 스크립트로 검증할 수 있습니다:

```python
from pathlib import Path
from PIL import Image

# 경로 설정
fold_A = Path("./portrait_retouch/A/train")
fold_B = Path("./portrait_retouch/B/train")

# A 폴더의 이미지 목록
images_A = sorted(fold_A.glob("*.jpg")) + sorted(fold_A.glob("*.png"))
images_B = sorted(fold_B.glob("*.jpg")) + sorted(fold_B.glob("*.png"))

print(f"A 폴더 이미지 개수: {len(images_A)}")
print(f"B 폴더 이미지 개수: {len(images_B)}")

# 파일명 매칭 확인
missing = []
for img_A in images_A:
    img_B = fold_B / img_A.name
    if not img_B.exists():
        missing.append(img_A.name)
        print(f"⚠️  매칭되지 않음: {img_A.name}")

if missing:
    print(f"\n❌ {len(missing)}개의 이미지가 매칭되지 않습니다!")
else:
    print("\n✅ 모든 이미지가 올바르게 매칭되었습니다!")

# 이미지 크기 확인
if images_A:
    img = Image.open(images_A[0])
    print(f"\n이미지 크기 예시: {img.size}")
```

## ⚠️ 주의사항

1. **파일명 일치**: A와 B의 파일명이 정확히 일치해야 합니다
2. **같은 인물**: 같은 파일명은 반드시 같은 인물이어야 합니다
3. **이미지 크기**: 두 이미지의 크기가 다르면 자동으로 조정되지만, 원본 크기가 같으면 좋습니다
4. **데이터 분할**: train, val, test 폴더로 나누면 더 좋습니다

## 📚 관련 문서

- 전체 데이터 준비 가이드: `DATA_PREPARATION_GUIDE.md`
- 학습/테스트 팁: `docs/tips.md`
- FAQ: `docs/qa.md`

