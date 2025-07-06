# AI Football Manager

AI 기반 축구 정보 통합 플랫폼 - 뉴스 분석, 경기 예측, 팀/선수 정보를 제공하는 지능형 축구 매니저

- **다중 도구 호출 지원**: 하나의 질문으로 여러 에이전트를 동시에 호출하여 통합된 답변 제공
- **확장 가능한 모듈형 설계**: 새로운 에이전트를 쉽게 추가 가능

## 목차
- [개요](#개요)
- [주요 기능](#주요-기능)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [사용법](#사용법)
- [기술 스택](#기술-스택)
- [API 설정](#api-설정)
- [아키텍처](#아키텍처)

## 개요

AI Football Manager는 OpenAI GPT-4o를 활용하여 축구 관련 질문을 지능적으로 분류하고, 각 분야별 전문 에이전트가 답변을 제공하는 멀티에이전트 시스템입니다.

### 핵심 특징
- **지능형 라우팅**: 질문 의도를 자동 분류하여 적절한 전문 에이전트로 연결
- **다중 도구 호출**: 복합 질문 시 여러 에이전트를 동시 실행하여 통합된 답변 제공
- **실시간 뉴스 분석**: 최신 축구 뉴스 검색, 요약, 감정 분석 및 AI 코멘트 제공
- **머신러닝 경기 예측**: soccerdata + api-football + 머신러닝 모델을 통한 예측 및 AI 해설
- **팀/선수 정보**: 상세한 팀 및 선수 데이터 제공
- **대화형 인터페이스**: Streamlit 기반 직관적인 채팅 UI
- **토큰 최적화**: 효율적인 API 사용

## 주요 기능

### 1. 뉴스 분석 에이전트
- **뉴스 검색**: News API를 통한 실시간 축구 뉴스 수집
- **기사 요약**: GPT-4o 기반 핵심 내용 요약
- **감정 분석**: 긍정/부정/중립 감정 자동 분류
- **AI 코멘트**: 전문가 수준의 분석 코멘트 생성

### 2. 경기 예측 에이전트
- **날짜/팀명 파싱**: 자연어 입력에서 경기 정보 자동 추출
- **데이터 수집**: Elo 레이팅, xG, 최근 폼 등 다양한 통계 수집
- **ML 예측**: 학습된 머신러닝 모델로 승부 확률 계산
- **전문가 해설**: 예측 근거와 관전 포인트 제공

### 3. 팀/선수 정보 에이전트
- **팀 정보**: 상세한 팀 데이터 및 통계
- **선수 프로필**: 개별 선수 정보 및 성과 분석
- **실시간 데이터**: API를 통한 최신 정보 제공

### 4. 지능형 라우터 (다중 도구 호출 지원)
- **단일 호출**: 하나의 전문 에이전트로 라우팅
- **다중 호출**: 복합 질문 시 여러 에이전트 동시 실행
- **결과 통합**: OpenAI를 통한 여러 에이전트 결과의 일관된 통합

## 프로젝트 구조

```
AI-Football-Manager/
├── ai_football_manager/          # 메인 애플리케이션 패키지
│   ├── agents/                   # AI 에이전트 모듈
│   │   ├── router_agent.py       # 질문 분류 및 라우팅 (다중 도구 호출 지원)
│   │   ├── news_analysis_agent.py # 뉴스 분석 전문 에이전트
│   │   ├── prediction_agent.py   # 경기 예측 전문 에이전트
│   │   ├── team_player_agent.py  # 팀/선수 정보 전문 에이전트
│   │   └── __init__.py
│   │
│   ├── tools/                    # 데이터 처리 도구
│   │   ├── news_tools.py         # 뉴스 검색/분석 도구
│   │   ├── prediction_tools.py   # 예측 관련 통합 도구
│   │   ├── match_parser.py       # 경기 정보 파싱 (날짜/팀명)
│   │   ├── data_collector_tools.py # 축구 데이터 수집 (Elo, xG 등)
│   │   ├── model_predictor.py    # ML 모델 예측 실행
│   │   ├── data_parser.py        # 데이터 파싱 유틸리티
│   │   └── sports_data_api.py    # 스포츠 데이터 API 인터페이스
│   │
│   ├── utils/                    # 유틸리티 모듈
│   │   ├── prompt_templates.py   # AI 프롬프트 템플릿
│   │   └── token_manager.py      # OpenAI 토큰 관리
│   │
│   ├── images/                   # 이미지 리소스
│   │   └── soccer.jpg
│   │
│   ├── models/                   # 머신러닝 모델 저장소
│   │
│   ├── app.py                    # Streamlit 웹 애플리케이션
│   ├── config.py                 # 환경 설정 (API 키 등)
│   ├── __main__.py               # 진입점
│   └── __init__.py
│
├── requirements.txt              # 의존성 패키지
├── README.md                     # 프로젝트 문서
└── .gitignore                    # Git 제외 파일
```

## 설치 및 실행
### 이 프로젝트는 **Python 3.9.13** 에서 구현되었습니다

### 1. 저장소 클론
```bash
git clone <repository-url>
cd AI-Football-Manager
```

### 2. 가상환경 생성 (권장)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
프로젝트 루트에 `.env` 파일 생성:
```env
OPENAI_API_KEY=your_openai_api_key_here
NEWS_API_KEY=your_news_api_key_here
X_RAPIDAPI_KEY=your_rapidapi_key_here
```

### 5. 애플리케이션 실행
```bash
# 방법 1: Python 모듈로 실행 (권장)
python -m ai_football_manager

# 방법 2: Streamlit 직접 실행
streamlit run ai_football_manager/app.py

# 방법 3: __main__.py 직접 실행
python ai_football_manager/__main__.py
```

브라우저에서 `http://localhost:8501` 접속

## 사용법

### 단일 에이전트 호출 예시

#### 뉴스 분석
```
"오늘 프리미어리그 소식을 알려줘"
"토트넘 최근 뉴스를 분석해줘"
```

#### 경기 예측 (경기일자, 팀이름)
```
"5월 18일 아스널 경기 예측해줘"
```

#### 팀/선수 정보
```
"브라이턴 전적 알려줘"
"맨시티 팀 정보를 보여줘"
"리버풀 선수 명단을 알려줘"
```

### 다중 에이전트 호출 예시 (복합 질문)
```
"5월 25일 토트넘 경기 예측하고 상대팀인 브라이턴에 전적 분석해줘"
"아스널 팀 정보와 아스널 관련 뉴스를 같이 보여줘"
```

## 기술 스택

### AI/ML
- **OpenAI GPT-4**: 질문 분류, 뉴스 분석, 응답 생성, 다중 결과 통합
- **scikit-learn**: 머신러닝 모델 (경기 예측)
- **tiktoken**: OpenAI 토큰 계산 및 관리

### 데이터 수집
- **soccerdata**: 축구 통계 데이터 (Elo 레이팅, xG 등)
- **News API**: 실시간 뉴스 검색
- **API-Football**: 경기 일정 및 정보

### 웹 프레임워크
- **Streamlit**: 웹 애플리케이션 인터페이스
- **pandas**: 데이터 처리 및 분석

### 기타
- **python-dateutil**: 날짜 파싱
- **requests**: HTTP API 호출
- **joblib**: 모델 직렬화

## API 설정

### 필수 API 키

1. **OpenAI API Key** 
   - 획득: [OpenAI Platform](https://platform.openai.com/api-keys)
   - 용도: GPT-4o 모델 사용

2. **News API Key**
   - 획득: [News API](https://newsapi.org/register)
   - 용도: 실시간 뉴스 검색

3. **RapidAPI Key (API-Football)** 
   - 획득: [RapidAPI](https://rapidapi.com/api-sports/api/api-football)
   - 용도: 축구 경기 일정 및 정보

## 아키텍처

### 시스템 플로우 (다중 도구 호출 지원)
```
사용자 입력 → 라우터 에이전트 → [단일/다중] 전문 에이전트 → [직접 반환/통합] → AI 응답
```

### 상세 흐름도
```
1. 사용자 질문 입력
2. Router Agent: GPT-4o로 질문 의도 분류 및 도구 선택
   ├── 단일 도구 호출
   │   ├── NEWS_ANALYSIS → News Analysis Agent → 직접 반환
   │   ├── PREDICTION → Prediction Agent → 직접 반환
   │   ├── TEAM_PLAYER → Team Player Agent → 직접 반환
   │   └── GENERAL → 일반 응답 → 직접 반환
   └── 다중 도구 호출
       ├── 여러 에이전트 동시 실행
       ├── 각 에이전트 결과 수집
       └── OpenAI를 통한 결과 통합
3. 최종 AI 응답 반환
```

### 다중 도구 호출 프로세스
```
복합 질문 → 의도 분석 → 필요한 에이전트들 식별 → 병렬 실행 → 결과 통합 → 통합된 응답
```

### 뉴스 분석 프로세스
```
질문 → 검색어 추출 → 뉴스 검색 → 기사 요약/감정 분석/AI 코멘트 → 종합 응답
```

### 경기 예측 프로세스
```
질문 → 날짜/팀명 파싱 → 데이터 수집 → ML 모델 예측 → AI 해설 → 예측 결과
```

### 팀/선수 분석 프로세스
```
질문 → 팀/선수명 추출 → 데이터 수집 → 통계 분석 → AI 해설 → 정보 제공
```