# 학습 방향 확인 가이드

## ✅ 현재 학습 방향

**학습 옵션 확인**: `direction: AtoB`

**결론**: **A에서 B로 학습하고 있습니다** ✅

## 📋 상세 설명

### 1. 합쳐진 이미지 구조

합쳐진 이미지에서:
- **왼쪽 절반 (0 ~ w/2)**: 도메인 **A** = 보정 후 이미지
- **오른쪽 절반 (w/2 ~ w)**: 도메인 **B** = 보정 전 이미지

**코드 확인** (`data/aligned_dataset.py` 42-46줄):
```python
w, h = AB.size
w2 = int(w / 2)
A = AB.crop((0, 0, w2, h))      # 왼쪽 절반 = A (보정 후)
B = AB.crop((w2, 0, w, h))     # 오른쪽 절반 = B (보정 전)
```

### 2. 학습 방향: AtoB

**코드 확인** (`models/pix2pix_model.py` 81-88줄):
```python
AtoB = self.opt.direction == "AtoB"
self.real_A = input["A" if AtoB else "B"].to(self.device)  # 입력 = A
self.real_B = input["B" if AtoB else "A"].to(self.device)  # 정답 = B

# Forward pass
self.fake_B = self.netG(self.real_A)  # G(A) → B 생성
```

**Loss 계산** (`models/pix2pix_model.py` 111줄):
```python
self.loss_G_L1 = self.criterionL1(self.fake_B, self.real_B) * self.opt.lambda_L1
# 생성된 B와 실제 B를 비교: G(A) = B
```

### 3. 학습 과정 요약

```
합쳐진 이미지
┌─────────────────┬─────────────────┐
│   A (보정 후)   │   B (보정 전)   │
│   (왼쪽 절반)   │   (오른쪽 절반) │
└─────────────────┴─────────────────┘
        ↓
    [분리]
        ↓
┌──────────┐    ┌──────────┐
│   A      │ →  │   B      │
│ (입력)   │    │ (정답)   │
└──────────┘    └──────────┘
        ↓
    [Generator]
        ↓
┌──────────┐
│  fake_B  │  (생성된 보정 전)
└──────────┘
        ↓
    [Loss 계산]
        ↓
fake_B와 real_B 비교 → 학습
```

## ✅ 확인 결과

### 현재 설정
- **합쳐진 이미지**: 왼쪽 = A (보정 후), 오른쪽 = B (보정 전)
- **학습 방향**: `--direction AtoB`
- **학습 목표**: A (보정 후) → B (보정 전) 변환 학습

### 학습 내용
1. **입력**: A (보정 후 이미지, 왼쪽 절반)
2. **출력**: B (보정 전 이미지, 오른쪽 절반)
3. **목표**: Generator가 A를 입력받아 B를 생성하도록 학습
4. **Loss**: 생성된 B (`fake_B`)와 실제 B (`real_B`)를 비교

## 🔄 방향 변경 방법

만약 반대 방향(B → A)으로 학습하고 싶다면:

```bash
python train.py --dataroot ./portrait_retouch --name portrait_retouch_reverse --model pix2pix --direction BtoA ...
```

**주의**: 
- `--direction BtoA`로 변경하면 B (보정 전) → A (보정 후)로 학습됩니다
- 현재 목적(보정 후 → 보정 전)과는 반대입니다

## 📊 실제 데이터 매핑

### 현재 설정 (AtoB)

| 합쳐진 이미지 위치 | 도메인 | 내용 | 역할 |
|-------------------|--------|------|------|
| 왼쪽 절반 (0 ~ w/2) | A | 보정 후 | 입력 (real_A) |
| 오른쪽 절반 (w/2 ~ w) | B | 보정 전 | 정답 (real_B) |

### 학습 과정

1. **입력**: A (보정 후) → Generator
2. **생성**: Generator(A) = fake_B (생성된 보정 전)
3. **비교**: fake_B vs real_B (실제 보정 전)
4. **학습**: fake_B가 real_B에 가까워지도록 학습

## ✅ 최종 확인

**질문**: 지금 학습시키는 것이 A에서 B로 가게끔 되어있는게 맞아?

**답변**: **네, 맞습니다!** ✅

- ✅ 합쳐진 이미지: 왼쪽 = A (보정 후), 오른쪽 = B (보정 전)
- ✅ 학습 방향: `--direction AtoB`
- ✅ 학습 목표: A (보정 후) → B (보정 전) 변환
- ✅ 코드 동작: `self.fake_B = self.netG(self.real_A)` → G(A) = B

현재 설정이 **보정 후 → 보정 전** 변환을 학습하는 것이 맞습니다.

