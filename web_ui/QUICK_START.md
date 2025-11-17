# 빠른 시작 가이드

## ⚠️ "Failed to fetch" 오류 해결

웹 UI에서 "모델 목록을 불러올 수 없습니다: Failed to fetch" 오류가 발생하면:

### 1. 백엔드 서버 실행 확인

백엔드 서버가 실행 중이어야 합니다. 다음 중 하나를 실행하세요:

**방법 A: 배치 파일 사용 (권장)**
```
프로젝트 루트에서 run_web_ui.bat 더블클릭
또는
web_ui 폴더에서 run_all.bat 더블클릭
```

**방법 B: 수동 실행**
```bash
# 새 터미널 창에서
cd H:\Git_Root\pytorch-CycleGAN-and-pix2pix
python web_ui\src\backend\app.py
```

### 2. 백엔드 서버 확인

브라우저에서 다음 URL을 열어보세요:
- http://localhost:5000/api/health
- `{"status":"ok"}` 응답이 나와야 합니다

### 3. 두 서버 모두 실행 확인

✅ **프론트엔드**: http://localhost:3000 (Vite 개발 서버)
✅ **백엔드**: http://localhost:5000 (Flask 서버)

두 서버가 모두 실행 중이어야 웹 UI가 정상 작동합니다.

## 실행 순서

1. **백엔드 먼저 실행** (중요!)
   ```
   web_ui/run_backend.bat
   ```
   또는
   ```
   python web_ui/src/backend/app.py
   ```

2. **프론트엔드 실행**
   ```
   web_ui/run_frontend.bat
   ```
   또는
   ```
   cd web_ui
   npm run dev
   ```

3. **브라우저에서 확인**
   - http://localhost:3000 접속
   - 모델 목록이 자동으로 로드되어야 합니다

## 문제 해결

### 백엔드 서버가 시작되지 않는 경우

1. Python이 설치되어 있는지 확인:
   ```bash
   python --version
   ```

2. Flask가 설치되어 있는지 확인:
   ```bash
   python -c "import flask"
   ```
   오류가 나면:
   ```bash
   pip install -r web_ui/src/backend/requirements.txt
   ```

3. 포트 5000이 이미 사용 중인지 확인:
   - 다른 프로그램이 포트 5000을 사용 중일 수 있습니다
   - `app.py`의 마지막 줄에서 포트를 변경할 수 있습니다

### 프론트엔드가 백엔드에 연결하지 못하는 경우

1. 백엔드 서버가 실행 중인지 확인
2. 브라우저 개발자 도구(F12) → Network 탭에서 요청 확인
3. CORS 오류가 있는지 확인

