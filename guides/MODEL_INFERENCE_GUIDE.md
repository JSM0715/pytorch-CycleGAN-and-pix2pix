# 학습된 모델 사용 가이드

학습된 모델을 사용하여 새로운 이미지에 추론을 수행하는 방법입니다.

## 📋 기본 사용법

### 방법 1: 테스트 데이터셋 사용 (pix2pix)

학습 시 사용한 데이터셋 구조와 동일한 테스트 데이터가 있는 경우:

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch latest
```

**설명**:
- `--dataroot`: 테스트 데이터 경로 (train 폴더에 합쳐진 이미지들이 있어야 함)
- `--name`: 학습 시 사용한 실험 이름
- `--model pix2pix`: 모델 타입
- `--direction AtoB`: 보정 후(A) → 보정 전(B) 방향
- `--epoch latest`: 최신 체크포인트 사용 (또는 특정 에포크 번호, 예: `--epoch 200`)

**결과 위치**: `./results/portrait_retouch_reverse/test_latest/index.html`

### 방법 2: 단일 이미지 폴더 사용 (보정 후 이미지만 있는 경우)

보정 후 이미지만 있고 보정 전 이미지가 없는 경우:

```bash
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --epoch latest \
    --no_dropout
```

**설명**:
- `--model test`: 단일 이미지 추론 모드
- `--dataset_mode single`: 단일 이미지 모드 (보정 후 이미지만 필요)
- `--no_dropout`: 드롭아웃 비활성화 (테스트 시 권장)

**폴더 구조**:
```
test_images/
├── image1.jpg    # 보정 후 이미지
├── image2.jpg
└── ...
```

## 🔧 주요 옵션

### 에포크 선택
```bash
--epoch latest      # 최신 체크포인트
--epoch 200         # 특정 에포크 번호
--load_iter 5000    # 특정 iteration (save_by_iter 사용 시)
```

### 결과 저장 위치
```bash
--results_dir ./my_results    # 기본값: ./results/
```

### 테스트할 이미지 개수
```bash
--num_test 100    # 기본값: 50
```

### 평가 모드
```bash
--eval    # eval 모드 사용 (batchnorm/dropout 동작 변경)
```

## 📁 데이터 준비

### 케이스 1: 테스트 데이터셋이 있는 경우

학습 데이터와 동일한 구조:
```
portrait_retouch/
└── test/          # 또는 train 폴더 사용
    ├── test001.jpg   # 왼쪽: 보정 후, 오른쪽: 보정 전 (합쳐진 이미지)
    └── test002.jpg
```

### 케이스 2: 보정 후 이미지만 있는 경우

```
test_images/
├── retouched_001.jpg   # 보정 후 이미지만
├── retouched_002.jpg
└── ...
```

## 💻 실제 사용 예시

### 예시 1: 학습 데이터로 테스트

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch latest \
    --num_test 10
```

### 예시 2: 새로운 보정 후 이미지 변환

```bash
# 1. 보정 후 이미지들을 test_images 폴더에 준비
# test_images/
#   ├── new_photo1.jpg
#   └── new_photo2.jpg

# 2. 추론 실행
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --epoch latest \
    --no_dropout
```

### 예시 3: 특정 에포크 모델 사용

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch 150    # 150번 에포크 모델 사용
```

## 📊 결과 확인

### HTML 결과 확인

결과는 HTML 파일로 저장됩니다:
```
./results/portrait_retouch_reverse/test_latest/index.html
```

브라우저에서 열어서 확인할 수 있습니다.

### 이미지 파일 위치

개별 이미지 파일은 다음 위치에 저장됩니다:
```
./results/portrait_retouch_reverse/test_latest/images/
├── image001_real_A.png    # 입력 이미지 (보정 후)
├── image001_fake_B.png    # 생성된 이미지 (보정 전)
└── image001_real_B.png    # 실제 이미지 (보정 전, 있는 경우)
```

## ⚙️ 고급 옵션

### 네트워크 아키텍처 지정

학습 시 사용한 아키텍처와 동일하게 지정:
```bash
--netG unet_256        # Generator 아키텍처
--norm batch           # Normalization 타입
--no_dropout           # 드롭아웃 비활성화
```

### 이미지 크기 조정

```bash
--load_size 512        # 로드 크기
--crop_size 512        # 크롭 크기 (load_size와 같게 설정)
--preprocess none      # 전처리 없음 (원본 크기 유지)
```

## 🔍 문제 해결

### 체크포인트를 찾을 수 없는 경우

```bash
# 체크포인트 위치 확인
ls ./checkpoints/portrait_retouch_reverse/

# 특정 에포크가 있는지 확인
ls ./checkpoints/portrait_retouch_reverse/*.pth
```

### 모델 아키텍처 불일치 오류

학습 시 사용한 옵션과 동일하게 지정:
```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --netG unet_256 \
    --norm batch \
    --no_dropout \
    --epoch latest
```

## 📝 빠른 참조

### 가장 간단한 명령어

```bash
# 학습 데이터로 테스트
python test.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction AtoB

# 새로운 이미지 변환
python test.py --dataroot ./test_images --name portrait_retouch_reverse --model test --dataset_mode single --no_dropout
```

## 🎯 체크리스트

테스트 전 확인사항:
- [ ] 체크포인트 파일이 존재하는가? (`./checkpoints/portrait_retouch_reverse/`)
- [ ] 테스트 이미지가 준비되었는가?
- [ ] 모델 아키텍처 옵션이 학습 시와 일치하는가?
- [ ] `--direction`이 올바른가? (AtoB: 보정 후 → 보정 전)

