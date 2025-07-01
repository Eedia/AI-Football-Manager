# AI-Football-Manager
sk rookies 모듈 프로젝트 1차_2조

# 개발 흐름 정리
- 데이터셋과 불필요한 파일들은 올리지 말기
- .env 당연히 올리지 말기 (API 키)

## 브랜치 전략
- **main**: 발표 용 (최종완성 코드), 항상 안정된 코드만 유지
- **develop**: 기능/버그 브랜치를 합치는 중간 브랜치
- **feature/기능명**: 새 기능 개발용 브랜치 (develop에서 생성 브랜치 생성)

## 기본 개발 흐름
1. **develop에서 브랜치 생성**
    ```bash
    git checkout develop
    git pull origin develop
    git checkout -b feature/기능명
    ```

2. **작업/커밋/푸시**
    ```bash
    git add .
    git commit -m "feat: 기능 추가"
    git push origin feature/기능명
    ```

3. **PR(Pull Request) 생성**
    - **feature/기능명 → develop** 으로 PR 요청
    - 코드 리뷰 후 merge

4. **모든 기능이 합쳐진 develop을 main에 머지**  
    - 배포 시점에만 진행


## 커밋 & PR 규칙

- 커밋 메시지: `feat: 기능 설명`, `fix: 버그 설명` 등
- PR 없이 main 직접 push 금지
- 모든 PR은 리뷰 후 merge