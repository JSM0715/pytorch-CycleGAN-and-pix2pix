from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
import os
from pathlib import Path
import re
from model_inference import run_inference

app = Flask(__name__)
# CORS 설정: localhost와 127.0.0.1 모두 허용
CORS(app, origins=[
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001"
])

# 프로젝트 루트 경로 계산
# app.py 위치: web_ui/src/backend/app.py
# 상위 4단계: web_ui/src/backend -> web_ui/src -> web_ui -> 프로젝트 루트
_current_file = Path(__file__).resolve()
PROJECT_ROOT = _current_file.parent.parent.parent.parent

# 여러 방법으로 경로 확인
# 방법 1: 상대 경로로 계산
if not (PROJECT_ROOT / 'checkpoints').exists():
    # 방법 2: 현재 작업 디렉토리 기준
    cwd = Path.cwd()
    if (cwd / 'checkpoints').exists():
        PROJECT_ROOT = cwd
    # 방법 3: 상위 디렉토리 확인
    elif (cwd.parent / 'checkpoints').exists():
        PROJECT_ROOT = cwd.parent

CHECKPOINT_DIR = PROJECT_ROOT / 'checkpoints' / 'portrait_retouch_reverse'

# 디버깅용 로그
print(f"[INIT] Current file: {_current_file}")
print(f"[INIT] PROJECT_ROOT: {PROJECT_ROOT}")
print(f"[INIT] CHECKPOINT_DIR: {CHECKPOINT_DIR}")
print(f"[INIT] CHECKPOINT_DIR exists: {CHECKPOINT_DIR.exists()}")
print(f"[INIT] Current working directory: {Path.cwd()}")

@app.route('/api/restore', methods=['POST'])
def restore_image():
    try:
        # 클라이언트에서 base64 인코딩된 이미지 받기
        data = request.json
        image_data = data.get('image')
        
        # 모델 및 파라미터 설정
        model_epoch = data.get('model', 'latest')
        direction = data.get('direction', 'AtoB')
        netG = data.get('netG', 'unet_256')
        norm = data.get('norm', 'batch')
        load_size = int(data.get('load_size', 1024))
        crop_size = int(data.get('crop_size', 1024))
        preprocess = data.get('preprocess', 'resize_and_crop')
        
        if not image_data:
            return jsonify({'error': '이미지가 없습니다'}), 400
        
        # base64 디코딩
        # data:image/png;base64, 부분 제거
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # 모델 추론 수행
        print(f"[INFO] Running inference with model={model_epoch}, direction={direction}, netG={netG}, norm={norm}")
        restored_image = run_inference(
            image_data=image_bytes,
            model_name='portrait_retouch_reverse',
            epoch=model_epoch,
            direction=direction,
            netG=netG,
            norm=norm,
            load_size=load_size,
            crop_size=crop_size,
            preprocess=preprocess
        )
        
        # 결과 이미지를 base64로 인코딩
        buffered = io.BytesIO()
        restored_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_str}'
        })
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] Exception in restore_image: {error_msg}")
        print(f"[ERROR] Traceback: {traceback_str}")
        return jsonify({'error': error_msg}), 500


@app.route('/api/models', methods=['GET'])
def get_available_models():
    """사용 가능한 모델 목록을 반환"""
    try:
        models = []
        
        # 경로 확인 및 디버깅
        print(f"[DEBUG] CHECKPOINT_DIR: {CHECKPOINT_DIR}")
        print(f"[DEBUG] CHECKPOINT_DIR exists: {CHECKPOINT_DIR.exists()}")
        print(f"[DEBUG] Current working directory: {Path.cwd()}")
        
        # 경로가 존재하지 않으면 재계산 시도
        checkpoint_dir = CHECKPOINT_DIR
        if not checkpoint_dir.exists():
            # 현재 작업 디렉토리 기준으로 재시도
            cwd = Path.cwd()
            alt_checkpoint = cwd / 'checkpoints' / 'portrait_retouch_reverse'
            if alt_checkpoint.exists():
                checkpoint_dir = alt_checkpoint
                print(f"[DEBUG] Using alternative checkpoint path: {checkpoint_dir}")
            else:
                # 상위 디렉토리 확인
                alt_checkpoint = cwd.parent / 'checkpoints' / 'portrait_retouch_reverse'
                if alt_checkpoint.exists():
                    checkpoint_dir = alt_checkpoint
                    print(f"[DEBUG] Using parent checkpoint path: {checkpoint_dir}")
        
        if not checkpoint_dir.exists():
            print(f"[ERROR] Checkpoint directory does not exist: {CHECKPOINT_DIR}")
            print(f"[ERROR] Tried alternative: {Path.cwd() / 'checkpoints' / 'portrait_retouch_reverse'}")
            return jsonify({
                'success': False,
                'error': f'Checkpoint directory not found: {CHECKPOINT_DIR}. Current dir: {Path.cwd()}',
                'models': []
            }), 404
        
        # latest 모델 확인
        latest_path = checkpoint_dir / 'latest_net_G.pth'
        print(f"[DEBUG] Checking latest model: {latest_path} (exists: {latest_path.exists()})")
        if latest_path.exists():
            models.append({
                'value': 'latest',
                'label': 'Latest (최신)',
                'description': '가장 최근에 학습된 모델'
            })
        
        # 에포크별 모델 찾기
        # *_net_G.pth 패턴의 파일 찾기
        pattern = re.compile(r'^(\d+)_net_G\.pth$')
        epochs = set()
        
        model_files = list(checkpoint_dir.glob('*_net_G.pth'))
        print(f"[DEBUG] Found {len(model_files)} model files in {checkpoint_dir}")
        
        for file in model_files:
            match = pattern.match(file.name)
            if match:
                epoch = int(match.group(1))
                epochs.add(epoch)
                print(f"[DEBUG] Found epoch model: {epoch}")
    
        # 에포크 번호로 정렬하여 추가
        for epoch in sorted(epochs, reverse=True):  # 최신 에포크부터
            models.append({
                'value': str(epoch),
                'label': f'Epoch {epoch}',
                'description': f'{epoch} 에포크 모델'
            })
        
        # JSM_Model 폴더 확인
        jsm_model_dir = checkpoint_dir / 'JSM_Model'
        if jsm_model_dir.exists():
            if (jsm_model_dir / 'latest_net_G.pth').exists() or (jsm_model_dir / '2000_net_G.pth').exists():
                models.append({
                    'value': 'JSM_Model',
                    'label': 'JSM Model',
                    'description': 'JSM 모델'
                })
        
        print(f"[DEBUG] Returning {len(models)} models")
        return jsonify({
            'success': True,
            'models': models
        })
    
    except Exception as e:
        import traceback
        error_msg = str(e)
        traceback_str = traceback.format_exc()
        print(f"[ERROR] Exception in get_available_models: {error_msg}")
        print(f"[ERROR] Traceback: {traceback_str}")
        return jsonify({
            'success': False,
            'error': error_msg,
            'models': []
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Allow connections from localhost (both 127.0.0.1 and localhost)
    # host='0.0.0.0' allows connections from all interfaces, but for security
    # we'll use '127.0.0.1' which should work with both localhost and 127.0.0.1
    app.run(debug=True, host='127.0.0.1', port=5000)
