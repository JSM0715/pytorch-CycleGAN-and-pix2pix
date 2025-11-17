# 이미지가 반으로 잘린 문제 해결

## 🔍 문제 원인

`aligned` 모드로 테스트하면 합쳐진 이미지(왼쪽: A, 오른쪽: B)를 자동으로 반으로 나눕니다:
- `real_A.png`: 합쳐진 이미지의 왼쪽 절반 (보정 후)
- `real_B.png`: 합쳐진 이미지의 오른쪽 절반 (보정 전, ground truth)
- `fake_B.png`: 생성된 보정 전 이미지

따라서 결과 이미지들이 반으로 잘린 것처럼 보이는 것은 **정상**입니다.

## ✅ 해결 방법

### 방법 1: 단일 이미지 모드 사용 (권장)

보정 후 이미지만 입력으로 주고 전체 크기의 보정 전 이미지를 얻으려면:

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

**폴더 구조**:
```
test_images/
├── retouched_photo1.jpg   # 보정 후 이미지만 (전체 크기)
├── retouched_photo2.jpg
└── ...
```

이렇게 하면 **전체 크기의 보정 전 이미지**가 생성됩니다.

### 방법 2: A, B 폴더 분리 사용

테스트용으로 A와 B를 분리된 폴더에 준비:

```
test_data/
├── testA/          # 보정 후 이미지들 (전체 크기)
│   ├── img1.jpg
│   └── img2.jpg
└── testB/          # 보정 전 이미지들 (전체 크기, 선택사항)
    ├── img1.jpg
    └── img2.jpg
```

그리고 `unaligned` 모드로 테스트:

```bash
python test.py \
    --dataroot ./test_data \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --dataset_mode unaligned \
    --epoch latest
```

## 📝 실제 사용 예시

### 예시 1: 보정 후 이미지만 변환 (가장 일반적)

```bash
# 1. 보정 후 이미지들을 test_images 폴더에 준비
# test_images/
#   ├── photo1.jpg
#   └── photo2.jpg

# 2. 단일 이미지 모드로 테스트
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --epoch latest \
    --no_dropout
```

**결과**: `./results/portrait_retouch_reverse/test_latest/images/`에 전체 크기의 `fake_B.png` 파일들이 생성됩니다.

### 예시 2: 학습 데이터로 테스트 (합쳐진 이미지 사용)

합쳐진 이미지를 사용하되, 결과를 전체 크기로 보고 싶다면:

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch latest \
    --preprocess none \
    --load_size 512 \
    --crop_size 512
```

이 경우에도 결과는 반으로 나뉘지만, 원본 크기를 유지합니다.

## 🎯 권장 방법

**보정 후 이미지만 변환하고 싶다면** → **방법 1 (단일 이미지 모드)** 사용

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

## 📊 결과 비교

### Aligned 모드 (현재 사용 중)
- 입력: 합쳐진 이미지 (왼쪽: A, 오른쪽: B)
- 출력: 
  - `real_A.png`: 왼쪽 절반 (보정 후)
  - `real_B.png`: 오른쪽 절반 (보정 전, ground truth)
  - `fake_B.png`: 생성된 보정 전 (절반 크기)

### Single 모드 (권장)
- 입력: 보정 후 이미지 (전체 크기)
- 출력:
  - `fake_B.png`: 생성된 보정 전 (전체 크기) ✅

## 💡 추가 팁

### 이미지 크기 조정

더 큰 이미지를 처리하려면:

```bash
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --epoch latest \
    --no_dropout \
    --preprocess none \
    --load_size 1024 \
    --crop_size 1024
```

### 여러 이미지 일괄 처리

```bash
# test_images 폴더에 모든 보정 후 이미지를 넣고
python test.py \
    --dataroot ./test_images \
    --name portrait_retouch_reverse \
    --model test \
    --direction AtoB \
    --dataset_mode single \
    --epoch latest \
    --no_dropout \
    --num_test 1000  # 처리할 이미지 개수
```

