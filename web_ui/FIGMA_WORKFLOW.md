# Figma 워크플로우 가이드

이 프로젝트는 Figma에서 Vibe Coding으로 생성된 UI와 커스텀 기능을 함께 사용합니다. Figma에서 수정한 내용을 반영하면서도 커스텀 기능을 유지하는 방법을 안내합니다.

## 📁 프로젝트 구조

```
web_ui/src/
├── components/
│   ├── figma/              # Figma에서 생성된 원본 컴포넌트
│   │   └── ImageWithFallback.tsx
│   └── ui/                 # Figma에서 생성된 UI 컴포넌트 (shadcn/ui)
│       ├── button.tsx
│       ├── card.tsx
│       └── ...
├── layouts/                # Figma 레이아웃 (새로 생성)
│   └── PortraitRetouchLayout.tsx  # Figma에서 생성된 레이아웃
├── features/               # 커스텀 기능 (새로 생성)
│   ├── imageProcessing.ts  # 이미지 처리 로직
│   └── api.ts             # API 호출 로직
├── App.tsx                 # 메인 앱 (레이아웃 + 기능 결합)
└── ...
```

## 🔄 Figma 업데이트 워크플로우

### 방법 1: 레이어 구조 사용 (권장)

**장점:**
- Figma 레이아웃과 커스텀 로직이 완전히 분리됨
- Figma 업데이트 시 레이아웃만 교체하면 됨
- 커스텀 기능은 영향받지 않음

**구조:**
1. **Figma 레이아웃**: `layouts/PortraitRetouchLayout.tsx` (Figma에서 생성)
2. **커스텀 로직**: `features/` 폴더에 분리
3. **App.tsx**: 레이아웃과 로직을 결합

### 방법 2: Git 브랜치 전략

**브랜치 구조:**
```
main                    # 안정 버전
├── figma-updates       # Figma 업데이트 전용 브랜치
└── feature/custom     # 커스텀 기능 개발 브랜치
```

**워크플로우:**
1. Figma에서 새 코드를 받으면 `figma-updates` 브랜치에서 작업
2. 레이아웃 파일만 교체
3. `main` 브랜치로 머지 (커스텀 기능은 유지)

## 📝 Figma 업데이트 절차

### Step 1: 백업
```bash
# 현재 커스텀 기능 백업
git checkout -b backup-before-figma-update
git add .
git commit -m "Backup before Figma update"
```

### Step 2: Figma 코드 받기
1. Figma에서 새 코드를 다운로드
2. **중요**: `components/ui/` 폴더만 교체 (다른 파일은 건드리지 않음)
3. `components/figma/` 폴더도 업데이트된 경우 교체

### Step 3: 레이아웃 업데이트
- Figma에서 생성된 메인 레이아웃이 있다면 `layouts/` 폴더에 교체
- `App.tsx`는 커스텀 로직이 있으므로 **직접 수정하지 않음**

### Step 4: 테스트
```bash
npm run dev
# 모든 기능이 정상 작동하는지 확인
```

## ⚠️ 주의사항

### 절대 덮어쓰면 안 되는 파일들:
- ✅ `App.tsx` - 커스텀 로직 포함
- ✅ `features/` 폴더 전체
- ✅ `src/backend/` 폴더 전체
- ✅ `package.json` - 프로젝트 의존성 포함

### 안전하게 교체 가능한 파일들:
- ✅ `components/ui/*` - UI 컴포넌트만 교체
- ✅ `components/figma/*` - Figma 컴포넌트만 교체
- ✅ `layouts/*` - 레이아웃만 교체
- ✅ `styles/globals.css` - 스타일만 교체 (커스텀 스타일 확인 필요)

## 🛠️ 현재 프로젝트 적용 방법

현재 `App.tsx`에 Figma 레이아웃과 커스텀 로직이 함께 있습니다. 
다음 단계로 분리하는 것을 권장합니다:

1. **레이아웃 분리**: Figma에서 생성된 UI 구조를 `layouts/PortraitRetouchLayout.tsx`로 분리
2. **로직 분리**: API 호출 및 이미지 처리 로직을 `features/` 폴더로 분리
3. **App.tsx 간소화**: 레이아웃과 로직을 결합하는 역할만 수행

이렇게 하면 Figma 업데이트 시 레이아웃 파일만 교체하면 됩니다.

## 📚 추가 리소스

- [Figma Dev Mode](https://www.figma.com/developers/dev-mode)
- [Git 브랜치 전략 가이드](https://www.atlassian.com/git/tutorials/comparing-workflows)

