/**
 * Figma에서 생성된 레이아웃 컴포넌트
 * 
 * ⚠️ 주의: Figma에서 업데이트할 때 이 파일만 교체하세요.
 * props 인터페이스는 변경하지 마세요.
 */

import React from 'react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { ImageWithFallback } from '../components/figma/ImageWithFallback';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { Slider } from '../components/ui/slider';
import { Upload, Loader2, Settings } from 'lucide-react';
import { InferenceParams, INFERENCE_PARAMS_OPTIONS } from '../features/inferenceParams';

export interface PortraitRetouchLayoutProps {
  beforeImage: string | null;
  afterImage: string | null;
  isProcessing: boolean;
  error: string | null;
  selectedModel: string;
  availableModels: Array<{ value: string; label: string; description?: string }>;
  isLoadingModels?: boolean;
  inferenceParams: InferenceParams;
  onImageUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRestore: () => void;
  onReset: () => void;
  onModelChange: (model: string) => void;
  onParamsChange: (params: Partial<InferenceParams>) => void;
}

/**
 * 인물 복원 UI 레이아웃
 * 
 * 이 컴포넌트는 Figma에서 생성된 UI 구조를 나타냅니다.
 * 비즈니스 로직은 props를 통해 전달받습니다.
 */
export function PortraitRetouchLayout({
  beforeImage,
  afterImage,
  isProcessing,
  error,
  selectedModel,
  availableModels,
  isLoadingModels = false,
  inferenceParams,
  onImageUpload,
  onRestore,
  onReset,
  onModelChange,
  onParamsChange,
}: PortraitRetouchLayoutProps) {
  const [showAdvanced, setShowAdvanced] = React.useState(false);
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-slate-900 mb-3">인물사진 복원</h1>
          <p className="text-slate-600">보정 후 이미지를 업로드하면 보정 전 이미지로 변환됩니다</p>
        </div>

        {/* Model Selection & Parameters */}
        <div className="mb-6 space-y-4">
          <div className="flex justify-center">
            <Card className="p-4 w-full max-w-md">
              <div className="flex flex-col gap-2">
                <label className="text-sm font-medium text-slate-700">모델 선택</label>
                <Select 
                  value={selectedModel} 
                  onValueChange={onModelChange}
                  disabled={isLoadingModels || availableModels.length === 0}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue 
                      placeholder={
                        isLoadingModels 
                          ? "모델 목록 로딩 중..." 
                          : availableModels.length === 0 
                          ? "사용 가능한 모델이 없습니다"
                          : "모델을 선택하세요"
                      } 
                    />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.map((model) => (
                      <SelectItem key={model.value} value={model.value}>
                        {model.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </Card>
          </div>

          {/* Advanced Parameters */}
          <div className="flex justify-center">
            <Card className="p-4 w-full max-w-4xl">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Settings className="w-4 h-4 text-slate-600" />
                  <h3 className="text-sm font-medium text-slate-700">고급 설정</h3>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAdvanced(!showAdvanced)}
                >
                  {showAdvanced ? '숨기기' : '보기'}
                </Button>
              </div>

              {showAdvanced && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Direction */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-slate-600">변환 방향</label>
                    <Select 
                      value={inferenceParams.direction} 
                      onValueChange={(value) => onParamsChange({ direction: value as 'AtoB' | 'BtoA' })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {INFERENCE_PARAMS_OPTIONS.direction.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* NetG */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-slate-600">Generator 네트워크</label>
                    <Select 
                      value={inferenceParams.netG} 
                      onValueChange={(value) => onParamsChange({ netG: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {INFERENCE_PARAMS_OPTIONS.netG.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Norm */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-slate-600">정규화</label>
                    <Select 
                      value={inferenceParams.norm} 
                      onValueChange={(value) => onParamsChange({ norm: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {INFERENCE_PARAMS_OPTIONS.norm.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Preprocess */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-slate-600">전처리</label>
                    <Select 
                      value={inferenceParams.preprocess} 
                      onValueChange={(value) => onParamsChange({ preprocess: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {INFERENCE_PARAMS_OPTIONS.preprocess.map((opt) => (
                          <SelectItem key={opt.value} value={opt.value}>
                            {opt.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Load Size */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-slate-600">
                      로드 크기: {inferenceParams.load_size}px
                    </label>
                    <Slider
                      value={[inferenceParams.load_size]}
                      onValueChange={(values) => onParamsChange({ load_size: values[0] })}
                      min={256}
                      max={2048}
                      step={64}
                      disabled={isProcessing}
                    />
                  </div>

                  {/* Crop Size */}
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-medium text-slate-600">
                      크롭 크기: {inferenceParams.crop_size}px
                    </label>
                    <Slider
                      value={[inferenceParams.crop_size]}
                      onValueChange={(values) => onParamsChange({ crop_size: values[0] })}
                      min={256}
                      max={2048}
                      step={64}
                      disabled={isProcessing}
                    />
                  </div>
                </div>
              )}
            </Card>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-center">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Before Image */}
          <Card className="p-6">
            <div className="mb-4">
              <h2 className="text-slate-900 mb-2">Before</h2>
              <p className="text-slate-500">보정 후 이미지 (입력)</p>
            </div>
            <div className="aspect-[3/4] bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center border-2 border-dashed border-slate-300">
              {beforeImage ? (
                <ImageWithFallback
                  src={beforeImage}
                  alt="Before"
                  className="w-full h-full object-cover"
                />
              ) : (
                <label className="cursor-pointer flex flex-col items-center justify-center h-full w-full">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={onImageUpload}
                    className="hidden"
                  />
                  <Upload className="w-12 h-12 text-slate-400 mb-3" />
                  <span className="text-slate-500">클릭하여 이미지 업로드</span>
                </label>
              )}
            </div>
            {beforeImage && (
              <Button
                variant="outline"
                className="w-full mt-4"
                onClick={onReset}
              >
                다시 선택
              </Button>
            )}
          </Card>

          {/* After Image */}
          <Card className="p-6">
            <div className="mb-4">
              <h2 className="text-slate-900 mb-2">After</h2>
              <p className="text-slate-500">보정 전 이미지 (결과)</p>
            </div>
            <div className="aspect-[3/4] bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center border-2 border-dashed border-slate-300">
              {afterImage ? (
                <ImageWithFallback
                  src={afterImage}
                  alt="After"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="flex flex-col items-center justify-center text-slate-400">
                  <div className="w-12 h-12 mb-3 border-2 border-slate-300 rounded-full flex items-center justify-center">
                    <span className="text-slate-300">?</span>
                  </div>
                  <span className="text-slate-500">복원 대기 중</span>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Restore Button */}
        <div className="flex justify-center">
          <Button
            size="lg"
            onClick={onRestore}
            disabled={!beforeImage || isProcessing}
            className="px-12"
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                복원 중...
              </>
            ) : (
              '복원'
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}

