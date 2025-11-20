# 인물사진 복원 웹 애플리케이션

React 프론트엔드와 Flask 백엔드를 사용한 인물사진 복원 웹 애플리케이션입니다.

## 프로젝트 구조

```
├── App.tsx                          # 메인 React 컴포넌트 (비즈니스 로직)
├── components/
│   └── PortraitRetouchLayout.tsx   # UI 레이아웃 컴포넌트
├── backend/
│   ├── app.py                      # Flask 메인 서버
│   ├── models_interface.py         # AI 모델 인터페이스 정의
│   ├── model_implementations.py    # AI 모델 구현
│   ├── requirements.txt            # Python 패키지 목록
│   └── IMPLEMENTATION_GUIDE.md     # 모델 구현 가이드 ⭐
└── build/                          # React 빌드 결과물 (생성 필요)
```

## 🚀 빠른 시작

### 1단계: React 앱 빌드

Figma Make에서 프로젝트를 다운로드한 후:

```bash
# 프로젝트 루트 디렉토리에서
npm install
npm run build
```

빌드가 완료되면 `build/` 폴더가 생성됩니다.

### 2단계: Flask 백엔드 설정

```bash
# backend 디렉토리로 이동
cd backend

# 가상환경 생성 (선택사항이지만 권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 3단계: Flask 서버 실행

```bash
# backend 디렉토리에서
python app.py
```

서버가 시작되면 브라우저에서 `http://localhost:5000`으로 접속하세요.

## 🎨 주요 기능

- **AI 모델 선택**: 4가지 복원 모델 중 선택 가능
  - GFPGAN - 일반 복원
  - CodeFormer - 고품질 복원
  - RestoreFormer - 빠른 복원
  - Real-ESRGAN - 고해상도 복원

- **이미지 업로드**: Before 영역에 이미지를 업로드
- **복원 처리**: 선택한 AI 모델로 이미지 복원
- **결과 비교**: Before/After 이미지를 나란히 비교

## 🔧 AI 모델 구현하기

**현재는 임시 이미지 처리만 동작합니다.** 실제 AI 모델을 구현하려면:

1. **`backend/IMPLEMENTATION_GUIDE.md`를 읽어보세요** ⭐
2. `backend/model_implementations.py`에서 각 모델 클래스 구현
3. 필요한 패키지를 `requirements.txt`에 추가
4. 모델 가중치 파일 다운로드

### 구현 인터페이스

모든 AI 모델은 다음 3가지 메서드를 구현해야 합니다:

```python
class YourModel(RestorationModel):
    def load_model(self) -> None:
        """모델을 메모리에 로드"""
        pass
    
    def restore(self, image: Image.Image, **kwargs) -> Image.Image:
        """이미지를 복원"""
        pass
    
    def get_model_info(self) -> Dict[str, Any]:
        """모델 정보 반환"""
        pass
```

자세한 내용은 `backend/IMPLEMENTATION_GUIDE.md`를 참고하세요.

## 📡 API 엔드포인트

### POST /api/restore
이미지 복원을 처리합니다.

**요청 본문:**
```json
{
  "image": "data:image/png;base64,...",
  "model": "gfpgan"
}
```

**응답:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "model_info": {
    "name": "GFPGAN",
    "version": "1.4",
    "description": "일반적인 얼굴 복원 모델"
  }
}
```

### GET /api/models
사용 가능한 모델 목록을 반환합니다.

**응답:**
```json
{
  "success": true,
  "models": [
    {
      "type": "gfpgan",
      "name": "GFPGAN",
      "version": "1.4",
      "description": "일반적인 얼굴 복원 모델",
      "supported_formats": ["jpg", "jpeg", "png", "bmp"],
      "max_resolution": [2048, 2048]
    }
  ]
}
```

### GET /api/health
서버 상태를 확인합니다.

**응답:**
```json
{
  "status": "ok",
  "loaded_models": ["gfpgan", "codeformer"]
}
```

## 🔬 개발 모드

개발 중에는 React와 Flask를 별도로 실행할 수도 있습니다:

```bash
# 터미널 1: React 개발 서버
npm start

# 터미널 2: Flask 서버
cd backend
python app.py
```

이 경우 React는 `http://localhost:3000`, Flask는 `http://localhost:5000`에서 실행됩니다.

## 📝 TODO

- [x] UI/비즈니스 로직 분리
- [x] AI 모델 인터페이스 설계
- [x] Flask API 엔드포인트 구현
- [ ] 실제 AI 모델 통합 (GFPGAN, CodeFormer, 등)
- [ ] 모델별 파라미터 조정 UI 추가
- [ ] 처리 진행률 표시
- [ ] 이미지 용량 제한 추가
- [ ] 배치 처리 기능

## 🛠 기술 스택

- **프론트엔드**: React, TypeScript, Tailwind CSS
- **백엔드**: Flask, Python
- **이미지 처리**: Pillow (추후 AI 모델로 교체 예정)
- **아키텍처**: 인터페이스 기반 모델 팩토리 패턴

## 📚 추가 문서

- `backend/IMPLEMENTATION_GUIDE.md` - AI 모델 구현 상세 가이드
- `backend/models_interface.py` - 모델 인터페이스 정의
- `backend/model_implementations.py` - 모델 구현 템플릿