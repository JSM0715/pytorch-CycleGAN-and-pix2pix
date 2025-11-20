import { useState, useEffect } from 'react';
import { PortraitRetouchLayout } from './components/PortraitRetouchLayout';

// test.py 파라미터 타입 정의
export interface Pix2PixParams {
  model_name: string;
  model_type: string;
  direction: string;
  epoch: string;
  netG: string;
  norm: string;
  load_size: number;
  crop_size: number;
  preprocess: string;
  no_dropout: boolean;
}

export interface AvailableModel {
  name: string;
  epochs: string[];
  latest_epoch: string;
  checkpoint_path: string;
}

export default function App() {
  const [beforeImage, setBeforeImage] = useState<string | null>(null);
  const [afterImage, setAfterImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [availableModels, setAvailableModels] = useState<AvailableModel[]>([]);
  
  // test.py 파라미터 상태
  const [params, setParams] = useState<Pix2PixParams>({
    model_name: '',
    model_type: 'test',
    direction: 'AtoB',
    epoch: 'latest',
    netG: 'unet_256',
    norm: 'batch',
    load_size: 1024,
    crop_size: 1024,
    preprocess: 'resize_and_crop',
    no_dropout: true,
  });

  // 사용 가능한 모델 목록 가져오기
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch('/api/models');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.models.length > 0) {
            setAvailableModels(data.models);
            // 첫 번째 모델을 기본값으로 설정
            const firstModel = data.models[0];
            setSelectedModel(firstModel.name);
            setParams(prev => ({
              ...prev,
              model_name: firstModel.name,
              epoch: firstModel.latest_epoch
            }));
          }
        }
      } catch (err) {
        console.error('모델 목록 가져오기 실패:', err);
        setError('모델 목록을 불러올 수 없습니다');
      }
    };
    
    fetchModels();
  }, []);

  // 모델 선택 시 파라미터 업데이트
  const handleModelChange = (modelName: string) => {
    setSelectedModel(modelName);
    const model = availableModels.find(m => m.name === modelName);
    if (model) {
      setParams(prev => ({
        ...prev,
        model_name: model.name,
        epoch: model.latest_epoch
      }));
    }
  };

  const handleBeforeImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setBeforeImage(reader.result as string);
        setAfterImage(null); // 새 이미지 업로드 시 결과 초기화
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRestore = async (restoreParams?: Pix2PixParams) => {
    if (!beforeImage) return;
    
    setIsProcessing(true);
    setError(null);
    setAfterImage(null); // 이전 결과 초기화
    
    // 파라미터 병합 (전달된 파라미터가 있으면 사용, 없으면 기본값 사용)
    const finalParams = restoreParams || params;
    
    console.log('[Frontend] 이미지 복원 시작', { params: finalParams });
    
    try {
      const response = await fetch('/api/restore', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: beforeImage,
          params: finalParams
        })
      });
      
      console.log('[Frontend] 응답 상태:', response.status, response.statusText);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: '서버 오류가 발생했습니다' }));
        console.error('[Frontend] 서버 오류:', errorData);
        throw new Error(errorData.error || '이미지 복원에 실패했습니다');
      }
      
      const data = await response.json();
      console.log('[Frontend] 응답 데이터:', { success: data.success, hasImage: !!data.image, imageLength: data.image?.length });
      
      if (data.success) {
        if (data.image) {
          setAfterImage(data.image);
          console.log('[Frontend] 이미지 설정 완료');
        } else {
          throw new Error('이미지 데이터가 없습니다');
        }
      } else {
        throw new Error(data.error || '알 수 없는 오류가 발생했습니다');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '서버 연결에 실패했습니다';
      setError(errorMessage);
      console.error('[Frontend] 에러:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setBeforeImage(null);
    setAfterImage(null);
    setError(null);
  };

  return (
    <PortraitRetouchLayout
      beforeImage={beforeImage}
      afterImage={afterImage}
      isProcessing={isProcessing}
      error={error}
      selectedModel={selectedModel}
      availableModels={availableModels}
      onImageUpload={handleBeforeImageUpload}
      onRestore={handleRestore}
      onReset={handleReset}
      onModelChange={handleModelChange}
    />
  );
}