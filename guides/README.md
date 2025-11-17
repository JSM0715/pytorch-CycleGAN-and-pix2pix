# 가이드 문서 모음

인물 보정 후 → 보정 전 변환 모델 사용을 위한 가이드 문서들입니다.

## 📚 문서 목록

### 🚀 시작하기

1. **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 전체 사용 가이드 (가장 중요!)
   - 환경 구성
   - 합쳐진 이미지 생성
   - 학습하기
   - 학습된 모델 사용
   - 모든 명령어와 파라미터 설명 포함

### 🔧 환경 설정

2. **[VENV_SETUP.md](VENV_SETUP.md)** - venv 가상환경 설정 가이드
   - Windows/Linux/macOS venv 사용법
   - PyTorch 설치
   - 패키지 설치

### 📁 데이터 준비

3. **[DATA_PREPARATION_GUIDE.md](DATA_PREPARATION_GUIDE.md)** - 데이터 준비 전체 가이드
   - CycleGAN 데이터 준비
   - pix2pix 데이터 준비
   - 자체 데이터셋 준비 방법

4. **[PORTRAIT_RETOUCH_GUIDE.md](PORTRAIT_RETOUCH_GUIDE.md)** - 인물 보정 데이터 준비 가이드
   - 인물 보정 후 → 보정 전 변환을 위한 데이터 준비
   - A, B 폴더 구조
   - 이미지 합치기

5. **[COMBINED_IMAGE_SUPPORT.md](COMBINED_IMAGE_SUPPORT.md)** - 합쳐진 이미지 지원 확인
   - pix2pix가 합쳐진 이미지를 지원하는지 확인
   - 작동 원리 설명
   - 코드 분석

### 🎓 학습 관련

6. **[CONTINUE_TRAINING_GUIDE.md](CONTINUE_TRAINING_GUIDE.md)** - 이어서 학습하기
   - `--continue_train` 사용법
   - 특정 에포크에서 이어서 학습
   - 에포크 카운트 설정

7. **[TRAINING_DIRECTION_GUIDE.md](TRAINING_DIRECTION_GUIDE.md)** - 학습 방향 확인
   - AtoB vs BtoA 차이
   - 현재 학습 방향 확인
   - 방향 변경 방법

8. **[IMPROVING_TRAINING_RESULTS.md](IMPROVING_TRAINING_RESULTS.md)** - 학습 결과 개선
   - 데이터 부족 문제 해결
   - 하이퍼파라미터 조정
   - L1 Loss 가중치 조정

9. **[OVERFITTING_FOR_TEST.md](OVERFITTING_FOR_TEST.md)** - 과적합 모델 생성 (테스트용)
   - 테스트용 과적합 모델 만들기
   - 피부 질감 복원 강화
   - L1 Loss 극대화

### 🔍 모델 사용

10. **[MODEL_INFERENCE_GUIDE.md](MODEL_INFERENCE_GUIDE.md)** - 학습된 모델 사용
    - 단일 이미지 모드
    - 고해상도 이미지 변환
    - 특정 에포크 모델 사용

11. **[CHECK_MODEL.md](CHECK_MODEL.md)** - 모델 확인 및 관리
    - 모델 저장 위치
    - 모델 파일 확인
    - 모델 정보 확인

### 🐛 문제 해결

12. **[FIX_CROPPED_IMAGES.md](FIX_CROPPED_IMAGES.md)** - 이미지가 반으로 잘린 문제 해결
    - 문제 원인
    - 단일 이미지 모드 사용
    - 전체 크기 결과 얻기

## 📖 빠른 참조

### 처음 시작하는 경우
1. [USAGE_GUIDE.md](USAGE_GUIDE.md) 읽기
2. [VENV_SETUP.md](VENV_SETUP.md)로 환경 구성
3. [PORTRAIT_RETOUCH_GUIDE.md](PORTRAIT_RETOUCH_GUIDE.md)로 데이터 준비
4. [USAGE_GUIDE.md](USAGE_GUIDE.md)의 학습 섹션으로 학습 시작

### 문제가 발생한 경우
- 이미지가 반으로 잘림 → [FIX_CROPPED_IMAGES.md](FIX_CROPPED_IMAGES.md)
- 모델을 찾을 수 없음 → [CHECK_MODEL.md](CHECK_MODEL.md)
- 학습 결과가 좋지 않음 → [IMPROVING_TRAINING_RESULTS.md](IMPROVING_TRAINING_RESULTS.md)
- 이어서 학습하고 싶음 → [CONTINUE_TRAINING_GUIDE.md](CONTINUE_TRAINING_GUIDE.md)

### 특정 작업
- 과적합 모델 만들기 → [OVERFITTING_FOR_TEST.md](OVERFITTING_FOR_TEST.md)
- 학습 방향 확인 → [TRAINING_DIRECTION_GUIDE.md](TRAINING_DIRECTION_GUIDE.md)
- 합쳐진 이미지 지원 확인 → [COMBINED_IMAGE_SUPPORT.md](COMBINED_IMAGE_SUPPORT.md)

## 🎯 문서 구조

```
guides/
├── README.md (이 파일)
├── USAGE_GUIDE.md (전체 가이드)
├── VENV_SETUP.md
├── DATA_PREPARATION_GUIDE.md
├── PORTRAIT_RETOUCH_GUIDE.md
├── COMBINED_IMAGE_SUPPORT.md
├── CONTINUE_TRAINING_GUIDE.md
├── TRAINING_DIRECTION_GUIDE.md
├── IMPROVING_TRAINING_RESULTS.md
├── OVERFITTING_FOR_TEST.md
├── MODEL_INFERENCE_GUIDE.md
├── CHECK_MODEL.md
└── FIX_CROPPED_IMAGES.md
```

