/**
 * 추론 파라미터 타입 및 기본값 정의
 */

export interface InferenceParams {
  direction: 'AtoB' | 'BtoA';
  netG: 'unet_256' | 'unet_128' | 'resnet_9blocks' | 'resnet_6blocks';
  norm: 'batch' | 'instance' | 'none';
  load_size: number;
  crop_size: number;
  preprocess: 'resize_and_crop' | 'resize' | 'crop' | 'none';
}

export const DEFAULT_INFERENCE_PARAMS: InferenceParams = {
  direction: 'AtoB',
  netG: 'unet_256',
  norm: 'batch',
  load_size: 1024,
  crop_size: 1024,
  preprocess: 'resize_and_crop',
};

export const INFERENCE_PARAMS_OPTIONS = {
  direction: [
    { value: 'AtoB', label: 'A → B (보정 후 → 보정 전) [권장]' },
    { value: 'BtoA', label: 'B → A (보정 전 → 보정 후)' },
  ],
  netG: [
    { value: 'unet_256', label: 'U-Net 256' },
    { value: 'unet_128', label: 'U-Net 128' },
    { value: 'resnet_9blocks', label: 'ResNet 9 Blocks' },
    { value: 'resnet_6blocks', label: 'ResNet 6 Blocks' },
  ],
  norm: [
    { value: 'batch', label: 'Batch Normalization' },
    { value: 'instance', label: 'Instance Normalization' },
    { value: 'none', label: 'None' },
  ],
  preprocess: [
    { value: 'resize_and_crop', label: 'Resize and Crop' },
    { value: 'resize', label: 'Resize' },
    { value: 'crop', label: 'Crop' },
    { value: 'none', label: 'None' },
  ],
};

