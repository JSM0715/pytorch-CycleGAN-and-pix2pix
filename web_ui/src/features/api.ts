/**
 * API 호출 관련 함수들
 * Figma 업데이트 시 이 파일은 유지됩니다.
 */

const API_BASE_URL = 'http://localhost:5000';

export interface RestoreImageResponse {
  success: boolean;
  image?: string;
  error?: string;
}

export interface InferenceParams {
  direction?: 'AtoB' | 'BtoA';
  netG?: string;
  norm?: string;
  load_size?: number;
  crop_size?: number;
  preprocess?: string;
}

export async function restoreImage(
  imageData: string,
  model: string = 'latest',
  params?: InferenceParams
): Promise<RestoreImageResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/restore`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        image: imageData,
        model: model,
        ...params
      })
    });
    
    if (!response.ok) {
      throw new Error('이미지 복원에 실패했습니다');
    }
    
    const data = await response.json();
    
    if (data.success) {
      return {
        success: true,
        image: data.image
      };
    } else {
      throw new Error(data.error || '알 수 없는 오류가 발생했습니다');
    }
  } catch (err) {
    return {
      success: false,
      error: err instanceof Error ? err.message : '서버 연결에 실패했습니다'
    };
  }
}

export interface ModelOption {
  value: string;
  label: string;
  description?: string;
}

export interface ModelsResponse {
  success: boolean;
  models: ModelOption[];
  error?: string;
}

export async function getAvailableModels(): Promise<ModelsResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/models`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        models: [],
        error: errorData.error || `서버 오류 (${response.status}): ${response.statusText}`
      };
    }
    
    const data = await response.json();
    return data;
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : '알 수 없는 오류';
    
    // 네트워크 오류인 경우 더 자세한 메시지 제공
    if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
      return {
        success: false,
        models: [],
        error: `백엔드 서버에 연결할 수 없습니다. 백엔드 서버가 http://localhost:5000 에서 실행 중인지 확인하세요. (${errorMessage})`
      };
    }
    
    return {
      success: false,
      models: [],
      error: `서버 연결 실패: ${errorMessage}`
    };
  }
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    const data = await response.json();
    return data.status === 'ok';
  } catch {
    return false;
  }
}

