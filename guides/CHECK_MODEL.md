# 모델 확인 및 사용 가이드

## 📍 모델 저장 위치

학습된 모델은 다음 위치에 저장됩니다:

```
./checkpoints/[실험이름]/
```

**현재 모델 위치**:
```
./checkpoints/portrait_retouch_reverse/
```

## 📂 모델 파일 구조

### 체크포인트 파일들

- `latest_net_G.pth`: **최신 Generator 모델** (가장 최근에 저장된 모델)
- `latest_net_D.pth`: 최신 Discriminator 모델
- `[에포크]_net_G.pth`: 특정 에포크의 Generator 모델 (예: `200_net_G.pth`)
- `[에포크]_net_D.pth`: 특정 에포크의 Discriminator 모델

### 기타 파일들

- `train_opt.txt`: 학습 시 사용한 옵션 설정
- `loss_log.txt`: 학습 손실 로그
- `web/index.html`: 학습 중간 결과 시각화

## 🔍 모델 확인 방법

### 방법 1: 파일 탐색기에서 확인

```
checkpoints/
└── portrait_retouch_reverse/
    ├── latest_net_G.pth      ← 이것이 최신 모델!
    ├── latest_net_D.pth
    ├── 200_net_G.pth         ← 200번 에포크 모델
    ├── 200_net_D.pth
    └── ...
```

### 방법 2: 명령어로 확인

**Windows (PowerShell/CMD)**:
```powershell
dir checkpoints\portrait_retouch_reverse\*.pth
```

**Linux/macOS**:
```bash
ls checkpoints/portrait_retouch_reverse/*.pth
```

### 방법 3: Python으로 확인

```python
from pathlib import Path

checkpoint_dir = Path("./checkpoints/portrait_retouch_reverse")
model_files = list(checkpoint_dir.glob("*.pth"))

print(f"총 {len(model_files)}개의 모델 파일이 있습니다:")
for f in sorted(model_files):
    size_mb = f.stat().st_size / (1024 * 1024)
    print(f"  - {f.name} ({size_mb:.2f} MB)")
```

## ✅ 모델이 제대로 저장되었는지 확인

### 체크리스트

- [ ] `checkpoints/portrait_retouch_reverse/` 폴더가 존재하는가?
- [ ] `latest_net_G.pth` 파일이 있는가?
- [ ] 파일 크기가 0이 아닌가? (일반적으로 수십 MB 이상)
- [ ] 여러 에포크의 모델이 있는가?

### 파일 크기 확인

정상적인 모델 파일 크기:
- Generator (`*_net_G.pth`): 보통 50-200 MB
- Discriminator (`*_net_D.pth`): 보통 10-50 MB

## 🚀 모델 사용하기

### 기본 사용 (최신 모델)

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch latest
```

### 특정 에포크 모델 사용

```bash
python test.py \
    --dataroot ./portrait_retouch \
    --name portrait_retouch_reverse \
    --model pix2pix \
    --direction AtoB \
    --epoch 200    # 200번 에포크 모델 사용
```

## 📊 모델 정보 확인

### 학습 옵션 확인

```bash
# Windows
type checkpoints\portrait_retouch_reverse\train_opt.txt

# Linux/macOS
cat checkpoints/portrait_retouch_reverse/train_opt.txt
```

### 학습 손실 확인

```bash
# Windows
type checkpoints\portrait_retouch_reverse\loss_log.txt

# Linux/macOS
cat checkpoints/portrait_retouch_reverse/loss_log.txt
```

### 학습 중간 결과 확인

브라우저에서 열기:
```
checkpoints/portrait_retouch_reverse/web/index.html
```

## 🔧 모델 파일 관리

### 중요한 파일

- **`latest_net_G.pth`**: 항상 최신 모델 (가장 중요!)
- **`[에포크]_net_G.pth`**: 특정 시점의 모델 (백업용)

### 불필요한 파일

- `*_net_D.pth`: 테스트 시에는 Generator만 필요 (Discriminator는 학습에만 사용)
- 오래된 에포크 파일: 공간이 부족하면 삭제 가능

### 모델 백업

```bash
# Windows
xcopy checkpoints\portrait_retouch_reverse backup\portrait_retouch_reverse\ /E /I

# Linux/macOS
cp -r checkpoints/portrait_retouch_reverse backup/
```

## ⚠️ 문제 해결

### 모델 파일이 없는 경우

1. 학습이 완료되었는지 확인
2. `--save_epoch_freq` 옵션으로 저장 주기 확인
3. 학습 중 오류가 발생했는지 확인

### 모델을 로드할 수 없는 경우

1. 파일이 손상되었는지 확인 (파일 크기가 0이 아닌지)
2. 학습 시 사용한 옵션과 동일한지 확인
3. `--netG`, `--norm` 등 아키텍처 옵션이 일치하는지 확인

## 💡 팁

1. **최신 모델 사용**: `--epoch latest` 사용 (가장 간단)
2. **최고 성능 모델 찾기**: 여러 에포크를 테스트해보고 가장 좋은 결과를 선택
3. **모델 백업**: 중요한 모델은 별도로 백업
4. **공간 관리**: 오래된 에포크 파일은 삭제해도 됨 (최신 모델만 유지)

