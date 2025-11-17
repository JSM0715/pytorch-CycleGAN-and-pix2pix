# Web UI 실행 가이드

이 프로젝트는 React 프론트엔드와 Flask 백엔드로 구성되어 있습니다. 두 서버를 모두 실행해야 합니다.

## 사전 요구사항

1. **Node.js** (v16 이상 권장)
2. **Python** (3.8 이상)
3. **npm** 또는 **yarn**

## 실행 방법

### 방법 1: 배치 파일 사용 (Windows - 권장)

**가장 간단한 방법:**

1. **프로젝트 루트**에서 `run_web_ui.bat` 더블클릭
   - 또는 `web_ui` 폴더에서 `run_all.bat` 더블클릭
   - 프론트엔드와 백엔드가 자동으로 실행됩니다!

2. **의존성 설치가 필요한 경우:**
   - `web_ui/install_dependencies.bat` 실행

**개별 실행:**
- 프론트엔드만: `web_ui/run_frontend.bat`
- 백엔드만: `web_ui/run_backend.bat`

### 방법 2: 수동 실행

#### 1단계: 프론트엔드 설정 및 실행

1. `web_ui` 폴더로 이동:
   ```bash
   cd web_ui
   ```

2. 의존성 설치:
   ```bash
   npm install
   ```

3. 개발 서버 실행:
   ```bash
   npm run dev
   ```

   프론트엔드는 기본적으로 **http://localhost:3000**에서 실행됩니다.
   브라우저가 자동으로 열립니다.

#### 2단계: 백엔드 설정 및 실행

**새 터미널 창**을 열어서:

1. 프로젝트 루트로 이동:
   ```bash
   cd H:\Git_Root\pytorch-CycleGAN-and-pix2pix
   ```

2. Python 가상환경 활성화 (선택사항이지만 권장):
   ```bash
   # 가상환경이 있다면
   # Windows:
   .\venv\Scripts\activate
   # 또는
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. 백엔드 의존성 설치:
   ```bash
   pip install -r web_ui/src/backend/requirements.txt
   ```

4. Flask 서버 실행:
   ```bash
   python web_ui/src/backend/app.py
   ```

   백엔드는 **http://localhost:5000**에서 실행됩니다.

## 실행 확인

1. 프론트엔드: 브라우저에서 http://localhost:3000 접속
2. 백엔드: 브라우저에서 http://localhost:5000/api/health 접속하여 `{"status":"ok"}` 응답 확인

## 문제 해결

### 포트가 이미 사용 중인 경우

- 프론트엔드 포트 변경: `vite.config.ts`의 `server.port` 수정
- 백엔드 포트 변경: `app.py`의 마지막 줄 `port=5000` 수정

### CORS 오류가 발생하는 경우

백엔드의 `app.py`에서 `CORS(app)`이 이미 설정되어 있으므로 문제없어야 합니다.
만약 문제가 있다면:
```python
CORS(app, origins=["http://localhost:3000"])
```

### 의존성 설치 오류

- Node.js 버전 확인: `node --version`
- Python 버전 확인: `python --version`
- npm 캐시 클리어: `npm cache clean --force`

## 프로덕션 빌드

프론트엔드를 빌드하려면:
```bash
cd web_ui
npm run build
```

빌드된 파일은 `web_ui/build` 폴더에 생성됩니다.

