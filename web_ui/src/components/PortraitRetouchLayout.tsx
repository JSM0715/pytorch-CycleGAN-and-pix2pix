/**
 * Figma에서 생성된 레이아웃 컴포넌트
 * 
 * ⚠️ 주의: Figma에서 업데이트할 때 이 파일만 교체하세요.
 * props 인터페이스는 변경하지 마세요.
 */

import { Button } from './ui/button';
import { Card } from './ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "./ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog"
import { Input } from './ui/input';
import { Label } from './ui/label';
import { ImageWithFallback } from './figma/ImageWithFallback';
import { Upload, Loader2, Settings2 } from 'lucide-react';
import { useState } from 'react';
import * as React from 'react';

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

export interface PortraitRetouchLayoutProps {
  beforeImage: string | null;
  afterImage: string | null;
  isProcessing: boolean;
  error: string | null;
  selectedModel: string;
  availableModels: AvailableModel[];
  onImageUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onRestore: (params?: Pix2PixParams) => void;
  onReset: () => void;
  onModelChange: (value: string) => void;
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
  onImageUpload,
  onRestore,
  onReset,
  onModelChange,
}: PortraitRetouchLayoutProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  
  // 선택된 모델 정보 가져오기
  const selectedModelInfo = availableModels.find(m => m.name === selectedModel);
  
  const [params, setParams] = useState<Pix2PixParams>({
    model_name: selectedModel || '',
    model_type: 'test',
    direction: 'AtoB',
    epoch: selectedModelInfo?.latest_epoch || 'latest',
    netG: 'unet_256',
    norm: 'batch',
    load_size: 1024,
    crop_size: 1024,
    preprocess: 'resize_and_crop',
    no_dropout: true,
  });

  // 선택된 모델이 변경되면 파라미터 업데이트
  React.useEffect(() => {
    if (selectedModelInfo) {
      setParams(prev => ({
        ...prev,
        model_name: selectedModelInfo.name,
        epoch: selectedModelInfo.latest_epoch
      }));
    }
  }, [selectedModel, selectedModelInfo]);

  const handleRestoreClick = () => {
    setIsDialogOpen(true);
  };

  const handleConfirmRestore = () => {
    setIsDialogOpen(false);
    onRestore(params);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-slate-900 mb-3 font-bold text-3xl">인물사진 복원</h1>
          <p className="text-slate-600">사진을 업로드하고 복원 결과를 확인하세요</p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-center">
            {error}
          </div>
        )}

        {/* Model Selection & Controls */}
        <div className="max-w-md mx-auto mb-8 bg-white p-4 rounded-xl shadow-sm border border-slate-100">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-slate-600 min-w-fit">
              <Settings2 className="w-4 h-4" />
              <span className="text-sm font-medium">AI 모델 선택</span>
            </div>
            <Select value={selectedModel} onValueChange={onModelChange} disabled={availableModels.length === 0}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder={availableModels.length === 0 ? "모델 없음" : "모델 선택"} />
              </SelectTrigger>
              <SelectContent>
                {availableModels.length === 0 ? (
                  <SelectItem value="none" disabled>체크포인트를 찾을 수 없습니다</SelectItem>
                ) : (
                  availableModels.map((model) => (
                    <SelectItem key={model.name} value={model.name}>
                      {model.name} ({model.latest_epoch})
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>
          {availableModels.length === 0 && (
            <p className="text-xs text-red-500 mt-2 text-center">
              checkpoints 디렉토리에서 모델을 찾을 수 없습니다.
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Before Image */}
          <Card className="p-6">
            <div className="mb-4">
              <h2 className="text-slate-900 mb-2">Before</h2>
              <p className="text-slate-500">원본 이미지</p>
            </div>
            <div className="aspect-square bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center border-2 border-dashed border-slate-300">
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
              <p className="text-slate-500">복원된 이미지</p>
            </div>
            <div className="aspect-square bg-slate-100 rounded-lg overflow-hidden flex items-center justify-center border-2 border-dashed border-slate-300">
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
            onClick={handleRestoreClick}
            disabled={!beforeImage || isProcessing}
            className="px-12 py-6 text-lg shadow-lg hover:shadow-xl transition-all"
          >
            {isProcessing ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                AI가 복원 중입니다...
              </>
            ) : (
              '복원 시작하기'
            )}
          </Button>
        </div>

        {/* Parameters Dialog */}
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>모델 파라미터 설정</DialogTitle>
              <DialogDescription>
                pix2pix 모델에 필요한 파라미터를 설정하세요. test.py에서 사용하는 파라미터와 동일합니다.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* Model Name */}
              <div className="space-y-2">
                <Label htmlFor="model_name">모델 이름 (--name)</Label>
                <Select
                  value={params.model_name}
                  onValueChange={(value) => {
                    const model = availableModels.find(m => m.name === value);
                    setParams({ 
                      ...params, 
                      model_name: value,
                      epoch: model?.latest_epoch || params.epoch
                    });
                  }}
                >
                  <SelectTrigger id="model_name">
                    <SelectValue placeholder="모델 선택" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableModels.map((model) => (
                      <SelectItem key={model.name} value={model.name}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-slate-500">체크포인트 폴더 이름</p>
              </div>

              {/* Model Type */}
              <div className="space-y-2">
                <Label htmlFor="model_type">모델 타입 (--model)</Label>
                <Select
                  value={params.model_type}
                  onValueChange={(value) => setParams({ ...params, model_type: value })}
                >
                  <SelectTrigger id="model_type">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="test">test (단일 이미지)</SelectItem>
                    <SelectItem value="pix2pix">pix2pix (정렬된 쌍)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Direction */}
              <div className="space-y-2">
                <Label htmlFor="direction">변환 방향 (--direction)</Label>
                <Select
                  value={params.direction}
                  onValueChange={(value) => setParams({ ...params, direction: value })}
                >
                  <SelectTrigger id="direction">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="AtoB">AtoB (A → B)</SelectItem>
                    <SelectItem value="BtoA">BtoA (B → A)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Epoch */}
              <div className="space-y-2">
                <Label htmlFor="epoch">에포크 (--epoch)</Label>
                {selectedModelInfo && selectedModelInfo.epochs.length > 0 ? (
                  <Select
                    value={params.epoch}
                    onValueChange={(value) => setParams({ ...params, epoch: value })}
                  >
                    <SelectTrigger id="epoch">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedModelInfo.epochs.map((epoch) => (
                        <SelectItem key={epoch} value={epoch}>
                          {epoch}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                ) : (
                  <Input
                    id="epoch"
                    value={params.epoch}
                    onChange={(e) => setParams({ ...params, epoch: e.target.value })}
                    placeholder="latest"
                  />
                )}
                <p className="text-xs text-slate-500">사용 가능한 에포크 중 선택하거나 직접 입력</p>
              </div>

              {/* Generator Architecture */}
              <div className="space-y-2">
                <Label htmlFor="netG">Generator (--netG)</Label>
                <Select
                  value={params.netG}
                  onValueChange={(value) => setParams({ ...params, netG: value })}
                >
                  <SelectTrigger id="netG">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="unet_256">unet_256</SelectItem>
                    <SelectItem value="unet_128">unet_128</SelectItem>
                    <SelectItem value="resnet_9blocks">resnet_9blocks</SelectItem>
                    <SelectItem value="resnet_6blocks">resnet_6blocks</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Normalization */}
              <div className="space-y-2">
                <Label htmlFor="norm">정규화 (--norm)</Label>
                <Select
                  value={params.norm}
                  onValueChange={(value) => setParams({ ...params, norm: value })}
                >
                  <SelectTrigger id="norm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="batch">batch</SelectItem>
                    <SelectItem value="instance">instance</SelectItem>
                    <SelectItem value="none">none</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Load Size */}
              <div className="space-y-2">
                <Label htmlFor="load_size">로드 크기 (--load_size)</Label>
                <Input
                  id="load_size"
                  type="number"
                  value={params.load_size}
                  onChange={(e) => setParams({ ...params, load_size: parseInt(e.target.value) || 1024 })}
                />
              </div>

              {/* Crop Size */}
              <div className="space-y-2">
                <Label htmlFor="crop_size">크롭 크기 (--crop_size)</Label>
                <Input
                  id="crop_size"
                  type="number"
                  value={params.crop_size}
                  onChange={(e) => setParams({ ...params, crop_size: parseInt(e.target.value) || 1024 })}
                />
              </div>

              {/* Preprocess */}
              <div className="space-y-2">
                <Label htmlFor="preprocess">전처리 (--preprocess)</Label>
                <Select
                  value={params.preprocess}
                  onValueChange={(value) => setParams({ ...params, preprocess: value })}
                >
                  <SelectTrigger id="preprocess">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="resize_and_crop">resize_and_crop</SelectItem>
                    <SelectItem value="crop">crop</SelectItem>
                    <SelectItem value="scale_width">scale_width</SelectItem>
                    <SelectItem value="scale_width_and_crop">scale_width_and_crop</SelectItem>
                    <SelectItem value="none">none</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsDialogOpen(false)}
                disabled={isProcessing}
              >
                취소
              </Button>
              <Button
                onClick={handleConfirmRestore}
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    복원 중...
                  </>
                ) : (
                  '복원 시작'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
