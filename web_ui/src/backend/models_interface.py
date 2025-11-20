"""
인물사진 복원 모델 인터페이스

이 파일은 AI 모델들이 구현해야 할 인터페이스를 정의합니다.
실제 프로젝트에서는 이 인터페이스를 상속받아 각 모델을 구현하세요.
"""

from abc import ABC, abstractmethod
from PIL import Image
from typing import Dict, Any, Optional
from enum import Enum


class ModelType(Enum):
    """지원하는 AI 모델 타입"""
    GFPGAN = "gfpgan"
    CODEFORMER = "codeformer"
    RESTOREFORMER = "restoreformer"
    REAL_ESRGAN = "real-esrgan"


class RestorationModel(ABC):
    """
    이미지 복원 모델의 기본 인터페이스
    
    모든 복원 모델은 이 클래스를 상속받아 구현해야 합니다.
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'cpu'):
        """
        모델 초기화
        
        Args:
            model_path: 모델 가중치 파일 경로 (None이면 기본 경로 사용)
            device: 실행 디바이스 ('cpu' 또는 'cuda')
        """
        self.model_path = model_path
        self.device = device
        self.model = None
        
    @abstractmethod
    def load_model(self) -> None:
        """
        모델을 메모리에 로드합니다.
        
        Raises:
            Exception: 모델 로드 실패 시
        """
        pass
    
    @abstractmethod
    def restore(self, image: Image.Image, **kwargs) -> Image.Image:
        """
        이미지를 복원합니다.
        
        Args:
            image: 복원할 PIL Image 객체
            **kwargs: 모델별 추가 파라미터
                - scale: 업스케일 배율 (기본값: 2)
                - face_enhance: 얼굴 향상 여부 (기본값: True)
                - bg_enhance: 배경 향상 여부 (기본값: False)
        
        Returns:
            복원된 PIL Image 객체
            
        Raises:
            Exception: 이미지 복원 실패 시
        """
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        모델 정보를 반환합니다.
        
        Returns:
            모델 정보를 담은 딕셔너리
            {
                'name': str,
                'version': str,
                'description': str,
                'supported_formats': List[str],
                'max_resolution': Tuple[int, int]
            }
        """
        pass
    
    def preprocess(self, image: Image.Image) -> Image.Image:
        """
        이미지 전처리 (선택적 구현)
        
        Args:
            image: 원본 이미지
            
        Returns:
            전처리된 이미지
        """
        # RGB 모드로 변환
        if image.mode != 'RGB':
            image = image.convert('RGB')
        return image
    
    def postprocess(self, image: Image.Image) -> Image.Image:
        """
        이미지 후처리 (선택적 구현)
        
        Args:
            image: 복원된 이미지
            
        Returns:
            후처리된 이미지
        """
        return image


class ModelFactory:
    """
    모델 인스턴스를 생성하는 팩토리 클래스
    """
    
    _models: Dict[str, type] = {}
    
    @classmethod
    def register_model(cls, model_type: str, model_class: type) -> None:
        """
        새로운 모델 클래스를 등록합니다.
        
        Args:
            model_type: 모델 타입 문자열 (예: 'gfpgan')
            model_class: RestorationModel을 상속받은 클래스
        """
        cls._models[model_type] = model_class
    
    @classmethod
    def create_model(cls, model_type: str, **kwargs) -> RestorationModel:
        """
        모델 인스턴스를 생성합니다.
        
        Args:
            model_type: 모델 타입 ('gfpgan', 'codeformer', 등)
            **kwargs: 모델 초기화 파라미터
            
        Returns:
            RestorationModel 인스턴스
            
        Raises:
            ValueError: 지원하지 않는 모델 타입인 경우
        """
        if model_type not in cls._models:
            raise ValueError(f"지원하지 않는 모델입니다: {model_type}. "
                           f"사용 가능한 모델: {list(cls._models.keys())}")
        
        model_class = cls._models[model_type]
        model_instance = model_class(**kwargs)
        model_instance.load_model()
        return model_instance
    
    @classmethod
    def get_available_models(cls) -> list:
        """
        사용 가능한 모든 모델 타입을 반환합니다.
        
        Returns:
            모델 타입 문자열 리스트
        """
        return list(cls._models.keys())


class RestorationConfig:
    """
    이미지 복원 설정을 관리하는 클래스
    """
    
    def __init__(
        self,
        scale: int = 2,
        face_enhance: bool = True,
        bg_enhance: bool = False,
        denoise_strength: float = 0.5,
        codeformer_fidelity: float = 0.5,
        max_image_size: int = 2048
    ):
        """
        Args:
            scale: 업스케일 배율 (1, 2, 4)
            face_enhance: 얼굴 향상 활성화 여부
            bg_enhance: 배경 향상 활성화 여부
            denoise_strength: 노이즈 제거 강도 (0.0 ~ 1.0)
            codeformer_fidelity: CodeFormer 충실도 (0.0 ~ 1.0)
            max_image_size: 최대 이미지 크기 (픽셀)
        """
        self.scale = scale
        self.face_enhance = face_enhance
        self.bg_enhance = bg_enhance
        self.denoise_strength = denoise_strength
        self.codeformer_fidelity = codeformer_fidelity
        self.max_image_size = max_image_size
    
    def to_dict(self) -> Dict[str, Any]:
        """설정을 딕셔너리로 변환"""
        return {
            'scale': self.scale,
            'face_enhance': self.face_enhance,
            'bg_enhance': self.bg_enhance,
            'denoise_strength': self.denoise_strength,
            'codeformer_fidelity': self.codeformer_fidelity,
            'max_image_size': self.max_image_size
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'RestorationConfig':
        """딕셔너리로부터 설정 생성"""
        return cls(**config_dict)
