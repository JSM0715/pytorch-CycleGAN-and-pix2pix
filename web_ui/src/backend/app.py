from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from PIL import Image
import io
import base64
import os
from pathlib import Path
from pix2pix_inference import Pix2PixInference

app = Flask(__name__, static_folder='../build', static_url_path='')
CORS(app)  # React 앱에서 API 호출 허용

# 모델 캐시 (한 번 로드한 모델을 재사용)
model_cache = {}

# React 앱 서빙
@app.route('/')
def serve_react_app():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # API 경로가 아닌 경우에만 정적 파일 서빙
    if path.startswith('api/'):
        return jsonify({'error': 'Not found'}), 404
    
    file_path = os.path.join(app.static_folder, path)
    if os.path.exists(file_path):
        return send_from_directory(app.static_folder, path)
    else:
        # SPA를 위해 모든 경로를 index.html로 리다이렉트
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/restore', methods=['POST'])
def restore_image():
    try:
        # 클라이언트에서 base64 인코딩된 이미지 받기
        data = request.json
        image_data = data.get('image')
        params = data.get('params', {})
        
        # 모델 설정 파라미터
        model_name = params.get('model_name', 'portrait_retouch_reverse')
        model_type = params.get('model_type', 'test')
        direction = params.get('direction', 'AtoB')
        epoch = params.get('epoch', 'latest')
        netG = params.get('netG', 'unet_256')
        norm = params.get('norm', 'batch')
        load_size = params.get('load_size', 1024)
        crop_size = params.get('crop_size', 1024)
        preprocess = params.get('preprocess', 'resize_and_crop')
        no_dropout = params.get('no_dropout', True)
        
        if not image_data:
            return jsonify({'error': '이미지가 없습니다'}), 400
        
        # base64 디코딩
        # data:image/png;base64, 부분 제거
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # 모델 캐시 키 생성
        cache_key = f"{model_name}_{model_type}_{direction}_{epoch}"
        
        # 모델 로드 (캐시 사용)
        if cache_key not in model_cache:
            print(f"새 모델 로드: {cache_key}")
            model = Pix2PixInference(
                model_name=model_name,
                model_type=model_type,
                direction=direction,
                epoch=epoch,
                netG=netG,
                norm=norm,
                load_size=load_size,
                crop_size=crop_size,
                preprocess=preprocess,
                no_dropout=no_dropout
            )
            model.load_model()
            model_cache[cache_key] = model
        else:
            model = model_cache[cache_key]
        
        # 이미지 추론 수행
        print(f"[INFO] 이미지 추론 시작: {input_image.size}, mode: {input_image.mode}")
        try:
            restored_image = model.infer(input_image)
            print(f"[INFO] 이미지 추론 완료: {restored_image.size}, mode: {restored_image.mode}")
        except Exception as e:
            import traceback
            print(f"[ERROR] 추론 중 오류: {traceback.format_exc()}")
            raise
        
        # 결과 이미지를 base64로 인코딩
        buffered = io.BytesIO()
        # RGB 모드로 변환 (RGBA나 다른 모드일 경우)
        if restored_image.mode != 'RGB':
            print(f"[WARNING] 이미지 모드 변환: {restored_image.mode} -> RGB")
            restored_image = restored_image.convert('RGB')
        restored_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        print(f"[INFO] 이미지 인코딩 완료: {len(img_str)} bytes")
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_str}',
            'model_info': model.get_model_info()
        })
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"오류 발생: {error_trace}")
        return jsonify({'error': f'이미지 복원 중 오류 발생: {str(e)}'}), 500

@app.route('/api/models', methods=['GET'])
def get_available_models():
    """사용 가능한 체크포인트 목록 반환"""
    try:
        # 프로젝트 루트 찾기: checkpoints 디렉토리를 찾을 때까지 상위 디렉토리 탐색
        # app.py 위치: web_ui/src/backend/app.py
        # 프로젝트 루트: web_ui/src/backend -> src -> web_ui -> 프로젝트 루트 (3단계)
        current_file = Path(__file__).resolve()
        current_dir = current_file.parent  # backend
        
        # 최대 6단계까지 상위 디렉토리 탐색
        checkpoints_dir = None
        PROJECT_ROOT = None
        
        for i in range(6):
            potential_checkpoints = current_dir / 'checkpoints'
            print(f"[DEBUG] 탐색 중: {current_dir} -> {potential_checkpoints} (존재: {potential_checkpoints.exists()})")
            
            if potential_checkpoints.exists() and potential_checkpoints.is_dir():
                # checkpoints 디렉토리 안에 실제 모델 파일이 있는지 확인
                model_dirs = [d for d in potential_checkpoints.iterdir() if d.is_dir() and not d.name.startswith('.')]
                if model_dirs:
                    # 모델 디렉토리가 있고, 그 안에 체크포인트 파일이 있는지 확인
                    has_checkpoints = False
                    for model_dir in model_dirs[:3]:  # 처음 3개만 확인
                        checkpoint_files = list(model_dir.glob('*_net_G*.pth'))
                        if checkpoint_files:
                            has_checkpoints = True
                            print(f"[DEBUG] 체크포인트 파일 발견: {model_dir.name} ({len(checkpoint_files)}개)")
                            break
                    
                    if has_checkpoints:
                        checkpoints_dir = potential_checkpoints
                        PROJECT_ROOT = current_dir
                        print(f"[INFO] 유효한 checkpoints 디렉토리 발견: {checkpoints_dir}")
                        break
                    else:
                        print(f"[DEBUG] {potential_checkpoints}에 체크포인트 파일이 없음, 계속 탐색...")
            
            current_dir = current_dir.parent
        
        if checkpoints_dir is None:
            # checkpoints 디렉토리를 찾을 수 없음
            print(f"[ERROR] checkpoints 디렉토리를 찾을 수 없습니다. app.py 위치: {current_file}")
            return jsonify({
                'success': True,
                'models': [],
                'error': 'checkpoints 디렉토리를 찾을 수 없습니다'
            })
        
        print(f"[INFO] checkpoints 디렉토리 발견: {checkpoints_dir}")
        
        models = []
        
        if checkpoints_dir.exists():
            # checkpoints 디렉토리에서 모델 이름 찾기
            for model_dir in checkpoints_dir.iterdir():
                if model_dir.is_dir() and not model_dir.name.startswith('.'):
                    # 체크포인트 파일 확인 (*_net_G.pth 또는 *_net_G[model_suffix].pth)
                    checkpoint_files = list(model_dir.glob('*_net_G*.pth'))
                    print(f"[DEBUG] 모델 디렉토리: {model_dir.name}, 체크포인트 파일 수: {len(checkpoint_files)}")
                    
                    if checkpoint_files:
                        # 모든 에포크 찾기
                        epochs = []
                        for checkpoint_file in checkpoint_files:
                            # 파일명에서 에포크 추출
                            # 예: latest_net_G.pth -> latest
                            # 예: 200_net_G.pth -> 200
                            # 예: iter_5000_net_G.pth -> iter_5000
                            stem = checkpoint_file.stem
                            if '_net_G' in stem:
                                epoch_str = stem.split('_net_G')[0]
                                epochs.append(epoch_str)
                        
                        print(f"[DEBUG] 발견된 에포크: {epochs[:10]}... (총 {len(set(epochs))}개)")
                        
                        # 중복 제거 및 정렬
                        epochs = sorted(set(epochs), key=lambda x: (
                            x == 'latest',  # latest를 맨 앞으로
                            x.startswith('iter_'),  # iter_는 나중으로
                            int(x.split('_')[-1]) if x.startswith('iter_') else (int(x) if x.isdigit() else 0)
                        ), reverse=True)
                        
                        # 최신 체크포인트 찾기 (latest가 있으면 우선, 없으면 가장 최근 수정된 파일)
                        latest_file = None
                        latest_epoch = None
                        
                        # latest 파일 찾기
                        for cf in checkpoint_files:
                            if cf.stem.startswith('latest_net_G'):
                                latest_file = cf
                                latest_epoch = 'latest'
                                break
                        
                        # latest가 없으면 가장 최근 수정된 파일 사용
                        if latest_file is None:
                            latest_file = max(checkpoint_files, key=lambda p: p.stat().st_mtime)
                            latest_epoch = latest_file.stem.split('_net_G')[0]
                        
                        print(f"[DEBUG] 최신 체크포인트: {latest_file.name}, 에포크: {latest_epoch}")
                        
                        models.append({
                            'name': model_dir.name,
                            'epochs': epochs,
                            'latest_epoch': latest_epoch,
                            'checkpoint_path': str(latest_file)
                        })
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"오류 발생: {error_trace}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'loaded_models': list(model_cache.keys())
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)