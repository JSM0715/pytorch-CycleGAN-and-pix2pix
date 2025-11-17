# 문제 해결 가이드

## 모델 목록을 불러올 수 없는 경우

### 1. 백엔드 서버 확인

백엔드 서버가 실행 중인지 확인하세요:
- `run_web_ui.bat` 또는 `web_ui/run_backend.bat` 실행
- 브라우저에서 http://localhost:5000/api/health 접속
- `{"status":"ok"}` 응답이 나와야 함

### 2. 경로 문제 확인

백엔드 콘솔에서 다음 로그를 확인하세요:
```
[INIT] Current file: ...
[INIT] PROJECT_ROOT: ...
[INIT] CHECKPOINT_DIR: ...
[INIT] CHECKPOINT_DIR exists: True/False
```

만약 `CHECKPOINT_DIR exists: False`라면:
- `checkpoints/portrait_retouch_reverse` 폴더가 프로젝트 루트에 있는지 확인
- 백엔드 서버를 프로젝트 루트에서 실행했는지 확인

### 3. 수동으로 경로 확인

백엔드 콘솔에서 다음 명령어로 확인:
```python
from pathlib import Path
print(Path.cwd())
print((Path.cwd() / 'checkpoints' / 'portrait_retouch_reverse').exists())
```

### 4. 네트워크 오류

프론트엔드 개발자 도구(F12)의 Network 탭에서:
- `/api/models` 요청이 실패하는지 확인
- CORS 오류가 있는지 확인
- 응답 상태 코드 확인 (200이어야 함)

### 5. 백엔드 재시작

경로 문제가 있다면:
1. 백엔드 서버 종료
2. 프로젝트 루트에서 `python web_ui/src/backend/app.py` 실행
3. 콘솔 로그 확인

