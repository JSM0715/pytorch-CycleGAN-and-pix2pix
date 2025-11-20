# Web UI 실행 가이드

인물사진 복원 웹 UI를 브라우저에서 실행하는 방법입니다.

## 사전 요구사항

1. **Node.js 설치** (npm 포함)
   - https://nodejs.org/ 에서 다운로드
   - LTS 버전 권장

2. **Python 환경** (백엔드용)
   - Python 3.8 이상
   - Flask 및 기타 의존성 설치 필요

## 빠른 시작

### 1. 의존성 설치

```bash
cd web_ui
npm install
```

### 2. 개발 서버 실행

```bash
npm run dev
```

브라우저에서 `http://localhost:5173` 접속

### 3. 백엔드 서버 실행 (별도 터미널)

```bash
cd web_ui/src/backend
pip install -r requirements.txt
python app.py
```

백엔드는 `http://localhost:5000`에서 실행됩니다.

## 프로젝트 구조

```
web_ui/
├── src/
│   ├── App.tsx              # 메인 앱 컴포넌트
│   ├── main.tsx              # React 진입점
│   ├── components/
│   │   ├── PortraitRetouchLayout.tsx  # 메인 레이아웃
│   │   ├── ui/               # UI 컴포넌트들
│   │   └── figma/            # Figma 관련 컴포넌트
│   ├── backend/              # Flask 백엔드
│   └── styles/               # 스타일 파일
├── package.json
├── vite.config.ts
└── index.html
```

## 스크립트

- `npm run dev`: 개발 서버 시작 (포트 5173)
- `npm run build`: 프로덕션 빌드
- `npm run preview`: 빌드된 앱 미리보기

## 문제 해결

### npm이 설치되지 않은 경우
1. Node.js를 설치하세요: https://nodejs.org/
2. 설치 후 터미널을 재시작하세요

### 포트가 이미 사용 중인 경우
`vite.config.ts`에서 포트를 변경하세요:
```typescript
server: {
  port: 3000,  // 다른 포트로 변경
}
```

### 백엔드 연결 오류
- 백엔드 서버가 `http://localhost:5000`에서 실행 중인지 확인
- `vite.config.ts`의 proxy 설정 확인

