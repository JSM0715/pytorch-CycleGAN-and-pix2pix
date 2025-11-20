# test.py 파라미터 완전 가이드

이 문서는 `test.py` 스크립트에서 사용할 수 있는 모든 파라미터를 설명합니다.

## 목차
1. [기본 파라미터](#기본-파라미터)
2. [모델 파라미터](#모델-파라미터)
3. [데이터셋 파라미터](#데이터셋-파라미터)
4. [테스트 전용 파라미터](#테스트-전용-파라미터)
5. [네트워크 초기화 파라미터](#네트워크-초기화-파라미터)
6. [시각화 파라미터](#시각화-파라미터)
7. [기타 파라미터](#기타-파라미터)
8. [pix2pix 모델 전용 파라미터](#pix2pix-모델-전용-파라미터)

---

## 기본 파라미터

### `--dataroot` (필수)
- **타입**: 문자열 (필수)
- **기본값**: 없음
- **설명**: 테스트 이미지가 있는 디렉토리 경로
- **예시**: `--dataroot ./test_images/test`
- **참고**: 
  - `--dataset_mode single` 사용 시: 단일 이미지 폴더 경로
  - `--dataset_mode aligned` 사용 시: `trainA`, `trainB` 등의 하위 폴더 포함

### `--name`
- **타입**: 문자열
- **기본값**: `"experiment_name"`
- **설명**: 실험 이름. 체크포인트와 결과 저장 위치를 결정합니다
- **저장 위치**:
  - 모델: `./checkpoints/{name}/`
  - 결과: `./results/{name}/`
- **예시**: `--name portrait_retouch_reverse`

### `--checkpoints_dir`
- **타입**: 문자열
- **기본값**: `"./checkpoints"`
- **설명**: 모델 체크포인트가 저장된 디렉토리 경로
- **예시**: `--checkpoints_dir ./checkpoints`

---

## 모델 파라미터

### `--model`
- **타입**: 문자열
- **기본값**: `"test"` (test.py에서는 자동 설정)
- **선택값**: `cycle_gan` | `pix2pix` | `test` | `colorization`
- **설명**: 사용할 모델 타입
- **참고**: 
  - `test`: 단방향 추론 모드 (자동으로 `--dataset_mode single` 설정)
  - `pix2pix`: pix2pix 모델 사용
  - `cycle_gan`: CycleGAN 모델 사용
- **예시**: `--model test`

### `--direction`
- **타입**: 문자열
- **기본값**: `"AtoB"`
- **선택값**: `AtoB` | `BtoA`
- **설명**: 이미지 변환 방향
  - `AtoB`: A 도메인 → B 도메인
  - `BtoA`: B 도메인 → A 도메인
- **예시**: `--direction AtoB`

### `--input_nc`
- **타입**: 정수
- **기본값**: `3`
- **설명**: 입력 이미지의 채널 수
  - `3`: RGB 이미지
  - `1`: 그레이스케일 이미지
- **예시**: `--input_nc 3`

### `--output_nc`
- **타입**: 정수
- **기본값**: `3`
- **설명**: 출력 이미지의 채널 수
  - `3`: RGB 이미지
  - `1`: 그레이스케일 이미지
- **예시**: `--output_nc 3`

### `--ngf`
- **타입**: 정수
- **기본값**: `64`
- **설명**: Generator의 마지막 컨볼루션 레이어에서 사용하는 필터 수
- **효과**: 값이 클수록 더 복잡한 네트워크 (메모리 사용량 증가)
- **예시**: `--ngf 64`

### `--ndf`
- **타입**: 정수
- **기본값**: `64`
- **설명**: Discriminator의 첫 번째 컨볼루션 레이어에서 사용하는 필터 수
- **효과**: 값이 클수록 더 강력한 판별기 (메모리 사용량 증가)
- **예시**: `--ndf 64`

### `--netG`
- **타입**: 문자열
- **기본값**: `"resnet_9blocks"` (pix2pix는 `"unet_256"`)
- **선택값**: `resnet_9blocks` | `resnet_6blocks` | `unet_256` | `unet_128`
- **설명**: Generator 아키텍처
- **옵션 설명**:
  - `unet_256`: 256x256 이미지용 U-Net (pix2pix 기본값)
  - `unet_128`: 128x128 이미지용 U-Net
  - `resnet_9blocks`: 9개 ResNet 블록 (CycleGAN 기본값)
  - `resnet_6blocks`: 6개 ResNet 블록
- **예시**: `--netG unet_256`

### `--netD`
- **타입**: 문자열
- **기본값**: `"basic"`
- **선택값**: `basic` | `n_layers` | `pixel`
- **설명**: Discriminator 아키텍처
- **옵션 설명**:
  - `basic`: 70x70 PatchGAN (가장 일반적)
  - `n_layers`: 레이어 수를 `--n_layers_D`로 조절 가능
  - `pixel`: 픽셀 단위 판별
- **예시**: `--netD basic`

### `--n_layers_D`
- **타입**: 정수
- **기본값**: `3`
- **설명**: `--netD n_layers` 사용 시 Discriminator의 레이어 수
- **예시**: `--n_layers_D 3`

### `--norm`
- **타입**: 문자열
- **기본값**: `"instance"` (pix2pix는 `"batch"`)
- **선택값**: `instance` | `batch` | `none` | `syncbatch`
- **설명**: 정규화 방법
- **옵션 설명**:
  - `instance`: Instance Normalization (CycleGAN 기본값)
  - `batch`: Batch Normalization (pix2pix 기본값)
  - `none`: 정규화 없음
  - `syncbatch`: Synchronized Batch Normalization (멀티 GPU)
- **예시**: `--norm batch`

### `--no_dropout`
- **타입**: 플래그 (값 없음)
- **기본값**: False
- **설명**: Generator에서 dropout 비활성화
- **예시**: `--no_dropout`

---

## 데이터셋 파라미터

### `--dataset_mode`
- **타입**: 문자열
- **기본값**: `"unaligned"` (pix2pix는 `"aligned"`)
- **선택값**: `unaligned` | `aligned` | `single` | `colorization`
- **설명**: 데이터셋 로딩 방식
- **옵션 설명**:
  - `single`: 단일 이미지 세트 (A만 또는 B만)
  - `aligned`: 정렬된 이미지 쌍 (A-B 쌍)
  - `unaligned`: 비정렬 이미지 쌍
  - `colorization`: 컬러화용 데이터셋
- **예시**: `--dataset_mode single`

### `--load_size`
- **타입**: 정수
- **기본값**: `286` (test.py에서는 `crop_size`와 동일하게 설정됨)
- **설명**: 이미지 로드 시 리사이즈 크기 (픽셀)
- **예시**: `--load_size 1024`

### `--crop_size`
- **타입**: 정수
- **기본값**: `256`
- **설명**: 리사이즈 후 크롭 크기 (픽셀)
- **참고**: test.py에서는 `load_size`와 동일하게 설정하는 것이 권장됨
- **예시**: `--crop_size 1024`

### `--preprocess`
- **타입**: 문자열
- **기본값**: `"resize_and_crop"`
- **선택값**: `resize_and_crop` | `crop` | `scale_width` | `scale_width_and_crop` | `none`
- **설명**: 이미지 전처리 방법
- **옵션 설명**:
  - `resize_and_crop`: 리사이즈 후 크롭
  - `crop`: 크롭만 수행
  - `scale_width`: 너비 기준 스케일
  - `scale_width_and_crop`: 너비 기준 스케일 후 크롭
  - `none`: 전처리 없음
- **예시**: `--preprocess resize_and_crop`

### `--no_flip`
- **타입**: 플래그 (값 없음)
- **기본값**: False (test.py에서는 True로 자동 설정)
- **설명**: 이미지 뒤집기 비활성화
- **참고**: 테스트 시에는 일관된 결과를 위해 자동으로 비활성화됨
- **예시**: `--no_flip`

### `--serial_batches`
- **타입**: 플래그 (값 없음)
- **기본값**: False (test.py에서는 True로 자동 설정)
- **설명**: 배치를 순서대로 가져오기 (셔플링 비활성화)
- **참고**: 테스트 시에는 일관된 결과를 위해 자동으로 활성화됨
- **예시**: `--serial_batches`

### `--max_dataset_size`
- **타입**: 정수
- **기본값**: `float("inf")` (무제한)
- **설명**: 데이터셋에서 사용할 최대 샘플 수
- **예시**: `--max_dataset_size 100`

---

## 테스트 전용 파라미터

### `--results_dir`
- **타입**: 문자열
- **기본값**: `"./results/"`
- **설명**: 테스트 결과가 저장될 디렉토리 경로
- **저장 위치**: `{results_dir}/{name}/{phase}_{epoch}/`
- **예시**: `--results_dir ./results`

### `--aspect_ratio`
- **타입**: 실수
- **기본값**: `1.0`
- **설명**: 결과 이미지의 종횡비
- **예시**: `--aspect_ratio 1.0`

### `--phase`
- **타입**: 문자열
- **기본값**: `"test"`
- **설명**: 실험 단계 (train, val, test 등)
- **예시**: `--phase test`

### `--eval`
- **타입**: 플래그 (값 없음)
- **기본값**: False
- **설명**: 테스트 시 eval 모드 사용 (BatchNorm, Dropout 등 비활성화)
- **예시**: `--eval`

### `--num_test`
- **타입**: 정수
- **기본값**: `50`
- **설명**: 테스트할 이미지 수
- **예시**: `--num_test 100`

---

## 체크포인트 파라미터

### `--epoch`
- **타입**: 문자열
- **기본값**: `"latest"`
- **설명**: 로드할 체크포인트 에포크
- **옵션**:
  - `"latest"`: 가장 최근 모델
  - `"best"`: 가장 좋은 성능 모델
  - 숫자 문자열: 특정 에포크 (예: `"100"`, `"200"`)
- **예시**: `--epoch latest`

### `--load_iter`
- **타입**: 정수
- **기본값**: `0`
- **설명**: 로드할 반복(iteration) 번호
- **참고**: `load_iter > 0`이면 `iter_{load_iter}` 형식으로 로드, 아니면 `epoch` 사용
- **예시**: `--load_iter 5000`

---

## 네트워크 초기화 파라미터

### `--init_type`
- **타입**: 문자열
- **기본값**: `"normal"`
- **선택값**: `normal` | `xavier` | `kaiming` | `orthogonal`
- **설명**: 네트워크 가중치 초기화 방법
- **예시**: `--init_type normal`

### `--init_gain`
- **타입**: 실수
- **기본값**: `0.02`
- **설명**: `normal`, `xavier`, `orthogonal` 초기화의 스케일링 팩터
- **예시**: `--init_gain 0.02`

---

## 시각화 파라미터

### `--display_winsize`
- **타입**: 정수
- **기본값**: `256`
- **설명**: HTML 및 Visdom에서 표시할 이미지 창 크기
- **예시**: `--display_winsize 256`

---

## 기타 파라미터

### `--verbose`
- **타입**: 플래그 (값 없음)
- **기본값**: False
- **설명**: 더 자세한 디버깅 정보 출력
- **예시**: `--verbose`

### `--suffix`
- **타입**: 문자열
- **기본값**: `""`
- **설명**: 사용자 정의 접미사. `opt.name = opt.name + suffix` 형식
- **예시**: `--suffix "_test"`

### `--use_wandb`
- **타입**: 플래그 (값 없음)
- **기본값**: False
- **설명**: wandb 로깅 활성화
- **예시**: `--use_wandb`

### `--wandb_project_name`
- **타입**: 문자열
- **기본값**: `"CycleGAN-and-pix2pix"`
- **설명**: wandb 프로젝트 이름
- **예시**: `--wandb_project_name my_project`

---

## pix2pix 모델 전용 파라미터

pix2pix 모델은 기본 파라미터 외에 다음 기본값을 사용합니다:

### 기본값 변경 (자동 적용)
- `--norm`: `"batch"` (기본 `"instance"` 대신)
- `--netG`: `"unet_256"` (기본 `"resnet_9blocks"` 대신)
- `--dataset_mode`: `"aligned"` (기본 `"unaligned"` 대신)
- `--gan_mode`: `"vanilla"` (훈련 시만, 기본 `"lsgan"` 대신)
- `--pool_size`: `0` (훈련 시만, 기본 `50` 대신)

### `--lambda_L1` (훈련 시만 사용)
- **타입**: 실수
- **기본값**: `100.0`
- **설명**: L1 손실의 가중치
- **공식**: `Loss = GAN Loss + lambda_L1 * ||G(A)-B||_1`
- **효과**:
  - 값 증가 (200-1000): 더 정확한 픽셀 매칭, 선명한 결과
  - 값 감소 (50-10): 더 다양한 생성, 부드러운 결과
- **참고**: 테스트 시에는 사용되지 않음 (훈련 시에만 적용)
- **예시**: `--lambda_L1 100.0`

---

## 사용 예시

### 기본 pix2pix 테스트
```bash
python test.py ^
  --dataroot ./test_images/test ^
  --name portrait_retouch_reverse ^
  --model test ^
  --direction AtoB ^
  --dataset_mode single ^
  --epoch latest ^
  --netG unet_256 ^
  --norm batch
```

### 고해상도 테스트
```bash
python test.py ^
  --dataroot ./test_images/test ^
  --name portrait_retouch_reverse ^
  --model test ^
  --direction AtoB ^
  --dataset_mode single ^
  --epoch latest ^
  --netG unet_256 ^
  --norm batch ^
  --load_size 1024 ^
  --crop_size 1024 ^
  --preprocess resize_and_crop
```

### 특정 에포크 테스트
```bash
python test.py ^
  --dataroot ./test_images/test ^
  --name portrait_retouch_reverse ^
  --model test ^
  --direction AtoB ^
  --dataset_mode single ^
  --epoch 200 ^
  --netG unet_256 ^
  --norm batch
```

### eval 모드 사용
```bash
python test.py ^
  --dataroot ./test_images/test ^
  --name portrait_retouch_reverse ^
  --model test ^
  --direction AtoB ^
  --dataset_mode single ^
  --epoch latest ^
  --netG unet_256 ^
  --norm batch ^
  --eval
```

---

## 주의사항

1. **`--model test` 사용 시**: 자동으로 `--dataset_mode single`이 설정됩니다
2. **`load_size`와 `crop_size`**: test.py에서는 동일하게 설정하는 것이 권장됩니다
3. **`--no_flip`과 `--serial_batches`**: test.py에서 자동으로 True로 설정됩니다
4. **`--batch_size`**: test.py에서는 항상 1로 고정됩니다
5. **`--num_threads`**: test.py에서는 항상 0으로 고정됩니다
6. **pix2pix 기본값**: pix2pix 모델 사용 시 일부 파라미터가 자동으로 변경됩니다

---

## 결과 저장 위치

테스트 결과는 다음 위치에 저장됩니다:
```
{results_dir}/{name}/{phase}_{epoch}/index.html
```

예시:
```
./results/portrait_retouch_reverse/test_latest/index.html
```

HTML 파일에서 원본 이미지와 변환된 이미지를 비교할 수 있습니다.

