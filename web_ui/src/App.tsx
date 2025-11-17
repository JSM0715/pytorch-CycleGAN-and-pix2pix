/**
 * 메인 App 컴포넌트
 * 
 * 이 파일은 Figma 레이아웃과 커스텀 로직을 결합합니다.
 * Figma 업데이트 시 이 파일은 유지하고, layouts/PortraitRetouchLayout.tsx만 교체하세요.
 */

import { useState, useEffect } from 'react';
import { PortraitRetouchLayout } from './layouts/PortraitRetouchLayout';
import { restoreImage, getAvailableModels, ModelOption } from './features/api';
import { readImageAsDataURL, validateImageFile } from './features/imageProcessing';
import { DEFAULT_MODEL } from './features/models';
import { DEFAULT_INFERENCE_PARAMS, InferenceParams } from './features/inferenceParams';

export default function App() {
  const [beforeImage, setBeforeImage] = useState<string | null>(null);
  const [afterImage, setAfterImage] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>(DEFAULT_MODEL);
  const [availableModels, setAvailableModels] = useState<ModelOption[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [inferenceParams, setInferenceParams] = useState<InferenceParams>(DEFAULT_INFERENCE_PARAMS);

  // 컴포넌트 마운트 시 사용 가능한 모델 목록 가져오기
  useEffect(() => {
    const loadModels = async () => {
      setIsLoadingModels(true);
      setError(null); // 이전 에러 초기화
      
      try {
        const result = await getAvailableModels();
        console.log('Models API response:', result);
        
        if (result.success && result.models.length > 0) {
          setAvailableModels(result.models);
          // 기본 모델이 목록에 없으면 첫 번째 모델 선택
          if (!result.models.find(m => m.value === selectedModel)) {
            setSelectedModel(result.models[0].value);
          }
          setError(null); // 성공 시 에러 초기화
        } else {
          // 모델 로드 실패 시 기본 모델만 표시
          setAvailableModels([{
            value: 'latest',
            label: 'Latest (최신)',
            description: '가장 최근에 학습된 모델'
          }]);
          const errorMsg = result.error 
            ? `모델 목록을 불러올 수 없습니다: ${result.error}` 
            : '모델 목록을 불러올 수 없습니다. 기본 모델을 사용합니다.';
          setError(errorMsg);
          console.error('Failed to load models:', result);
        }
      } catch (err) {
        // 네트워크 오류 등
        setAvailableModels([{
          value: 'latest',
          label: 'Latest (최신)',
          description: '가장 최근에 학습된 모델'
        }]);
        let errorMsg = '모델 목록을 불러올 수 없습니다.';
        if (err instanceof Error) {
          if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
            errorMsg = '백엔드 서버에 연결할 수 없습니다. 백엔드 서버를 실행하세요:\n1. web_ui/run_backend.bat 실행\n2. 또는 프로젝트 루트에서: python web_ui/src/backend/app.py';
          } else {
            errorMsg = `모델 목록을 불러올 수 없습니다: ${err.message}`;
          }
        }
        setError(errorMsg);
        console.error('Error loading models:', err);
      } finally {
        setIsLoadingModels(false);
      }
    };

    loadModels();
  }, []);

  const handleBeforeImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 파일 검증
    const validation = validateImageFile(file);
    if (!validation.valid) {
      setError(validation.error || '파일 업로드에 실패했습니다');
      return;
    }

    // 이미지 읽기
    try {
      const dataUrl = await readImageAsDataURL(file);
      setBeforeImage(dataUrl);
      setError(null);
      setAfterImage(null); // 새 이미지 업로드 시 이전 결과 초기화
    } catch (err) {
      setError('이미지 읽기에 실패했습니다');
      console.error('Error reading image:', err);
    }
  };

  const handleRestore = async () => {
    if (!beforeImage) return;
    
    setIsProcessing(true);
    setError(null);
    
    const result = await restoreImage(beforeImage, selectedModel, inferenceParams);
    
    if (result.success && result.image) {
      setAfterImage(result.image);
    } else {
      setError(result.error || '이미지 복원에 실패했습니다');
      }
      
    setIsProcessing(false);
  };

  const handleParamsChange = (params: Partial<InferenceParams>) => {
    setInferenceParams(prev => ({ ...prev, ...params }));
    // 파라미터 변경 시 이전 결과 초기화
    setAfterImage(null);
  };

  const handleModelChange = (model: string) => {
    setSelectedModel(model);
    // 모델 변경 시 이전 결과 초기화
    setAfterImage(null);
    setError(null);
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
      isLoadingModels={isLoadingModels}
      inferenceParams={inferenceParams}
      onImageUpload={handleBeforeImageUpload}
      onRestore={handleRestore}
      onReset={handleReset}
      onModelChange={handleModelChange}
      onParamsChange={handleParamsChange}
    />
  );
}