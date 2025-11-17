# pix2pix 합쳐진 이미지 지원 가이드

## ✅ 지원 확인

**pix2pix는 합쳐진 이미지(왼쪽: A, 오른쪽: B)를 공식적으로 지원합니다.**

## 📋 작동 원리

### 1. 데이터셋 클래스: `AlignedDataset`

`data/aligned_dataset.py` 파일의 `AlignedDataset` 클래스가 합쳐진 이미지를 처리합니다.

**코드 확인** (`data/aligned_dataset.py` 39-46줄):
```python
# read a image given a random integer index
AB_path = self.AB_paths[index]
AB = Image.open(AB_path).convert("RGB")
# split AB image into A and B
w, h = AB.size
w2 = int(w / 2)
A = AB.crop((0, 0, w2, h))      # 왼쪽 절반 = A
B = AB.crop((w2, 0, w, h))     # 오른쪽 절반 = B
```

**설명**:
- 합쳐진 이미지를 읽어서 **가로로 반으로 나눕니다**
- 왼쪽 절반 (0 ~ w/2): 도메인 A
- 오른쪽 절반 (w/2 ~ w): 도메인 B

### 2. pix2pix 모델 설정

`models/pix2pix_model.py` 파일에서 기본값으로 `aligned` 모드를 사용합니다.

**코드 확인** (`models/pix2pix_model.py` 33줄):
```python
parser.set_defaults(norm="batch", netG="unet_256", dataset_mode="aligned")
```

**설명**:
- `dataset_mode="aligned"`: 정렬된 쌍 데이터 모드
- 이 모드가 합쳐진 이미지를 자동으로 처리합니다

## 📖 공식 문서 확인

### `docs/datasets.md` (33-44줄)

공식 문서에서 명확히 설명하고 있습니다:

> "We provide a python script to generate pix2pix training data in the form of pairs of images {A,B}, where A and B are two different depictions of the same underlying scene. For example, these might be pairs {label map, photo} or {bw image, color image}."
>
> "Once the data is formatted this way, call:
> ```bash
> python datasets/combine_A_and_B.py --fold_A /path/to/data/A --fold_B /path/to/data/B --fold_AB /path/to/data
> ```
>
> **This will combine each pair of images (A,B) into a single image file, ready for training.**"

### `docs/tips.md` (19-32줄)

학습 팁 문서에서도 동일하게 설명:

> "Pix2pix's training requires paired data. We provide a python script to generate training data in the form of pairs of images {A,B}..."
>
> "This will combine each pair of images (A,B) into a single image file, ready for training."

## 🔍 작동 방식 상세 설명

### 학습 과정

1. **이미지 로드**: 합쳐진 이미지 파일을 읽습니다
   - 예: `train/person001.jpg` (1024x512 크기, 왼쪽: 보정 후, 오른쪽: 보정 전)

2. **이미지 분리**: 가로로 반으로 나눕니다
   - A (보정 후): (0, 0) ~ (512, 512) - 왼쪽 절반
   - B (보정 전): (512, 0) ~ (1024, 512) - 오른쪽 절반

3. **전처리**: 두 이미지에 동일한 변환을 적용합니다
   - 리사이즈, 크롭, 플립 등 (동일한 파라미터 사용)

4. **학습**: pix2pix 모델이 A → B 변환을 학습합니다
   - Generator: A를 입력으로 받아 B를 생성
   - Discriminator: (A, B) 쌍이 진짜인지 판별
   - Loss: 생성된 B와 실제 B를 비교 (L1 Loss)

### 테스트 과정

1. **합쳐진 이미지 사용 시**: 학습과 동일하게 좌우로 나눕니다
2. **단일 이미지 사용 시**: `--dataset_mode single`로 보정 후 이미지만 사용

## ✅ 확인 방법

### 방법 1: 코드 확인

```python
# data/aligned_dataset.py 파일 확인
from data.aligned_dataset import AlignedDataset

# AlignedDataset 클래스의 __getitem__ 메서드 확인
# 42-46줄에서 합쳐진 이미지를 좌우로 나누는 코드 확인
```

### 방법 2: 실제 동작 확인

학습 중간 결과를 확인:
```
./checkpoints/portrait_retouch_reverse/web/index.html
```

이 파일에서:
- `real_A`: 합쳐진 이미지의 왼쪽 절반 (보정 후)
- `real_B`: 합쳐진 이미지의 오른쪽 절반 (보정 전, 정답)
- `fake_B`: 모델이 생성한 보정 전 이미지

### 방법 3: 공식 예제 확인

공식 README와 문서에서 합쳐진 이미지 사용을 권장합니다:
- `docs/datasets.md`: 공식 데이터셋 가이드
- `docs/tips.md`: 학습 팁
- `datasets/combine_A_and_B.py`: 합치기 스크립트 제공

## 📝 요약

| 항목 | 내용 |
|------|------|
| **지원 여부** | ✅ 공식 지원 |
| **데이터셋 모드** | `aligned` (기본값) |
| **처리 방식** | 합쳐진 이미지를 가로로 반으로 나눔 |
| **왼쪽 절반** | 도메인 A (입력) |
| **오른쪽 절반** | 도메인 B (출력/정답) |
| **공식 문서** | `docs/datasets.md`, `docs/tips.md` |
| **코드 위치** | `data/aligned_dataset.py` (39-46줄) |

## 💡 결론

**pix2pix는 합쳐진 이미지를 공식적으로 지원하며, 이것이 권장되는 데이터 준비 방식입니다.**

- ✅ 합쳐진 이미지 사용: 공식 지원, 권장 방식
- ✅ `combine_A_and_B.py` 스크립트: 공식 제공
- ✅ `AlignedDataset` 클래스: 합쳐진 이미지 자동 처리
- ✅ 공식 문서: 명확히 설명됨

따라서 현재 사용 중인 방식(합쳐진 이미지로 학습)은 **정확하고 권장되는 방법**입니다.

