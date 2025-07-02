# 축구 경기 승패 예측 모델 요약

## 1. 데이터셋 요약 (`EPL_2000_2025.csv`)

### 목적
- 축구 경기의 승패 예측, **홈팀 승리 여부**를 예측하는 데 사용되는 데이터셋

### 구조
- 행(row): 각 경기
- 열(column): 경기 정보, 팀 전력, 폼, xG, 베팅 확률 등

### 주요 피처 그룹

| 범주         | 주요 피처 |
|--------------|------------|
| 경기 정보     | `MatchDate`, `month`, `weekday` |
| 팀 이름       | `HomeTeam`, `AwayTeam` |
| 팀 전력       | `HomeElo`, `AwayElo`, `elo_diff`, `elo_change_home`, `elo_change_away` |
| 최근 폼       | `Form3Home`, `Form5Home`, `Form3Away`, `Form5Away` |
| 사전 확률     | `prob_home`, `prob_draw`, `prob_away` |
| xG 관련 지표 | `h_xg`, `a_xg`, `xG_diff`, `xg_margin`, `xg_ratio`, `rolling_xg_home_5`, `rolling_xg_away_5` |
| 결과         | `result`: 2=홈승, 1=원정승, 0=무승부 |

> 시즌 초 경기에는 xG, 폼 등 결측치가 다수 존재

---

## 2. 모델 코드 요약 (`xgb_predict.py`)

### 목적
- XGBoost를 사용하여 **홈팀이 승리할지 여부 (`result == 2`)**를 예측하는 이진 분류 모델

### 주요 처리 흐름

#### 1. 데이터 로딩 및 전처리
- 2021년 이후 경기만 사용  
  `df[df['MatchDate'].dt.year >= 2021]`
- 결측치 제거  
  `df.dropna(subset=features + ['result'])`

#### 2. 피처 선정
- Elo, Form, xG, 사전 확률 등 총 20개 피처 사용

#### 3. 타겟 라벨 정의
- `y = (df['result'] == 2).astype(int)`  
  → 1: 홈팀 승리, 0: 무/원정팀 승

#### 4. 모델 구성
- 모델: `xgboost.XGBClassifier`
- 주요 파라미터:
  - `n_estimators=100`
  - `max_depth=4`
  - `learning_rate=0.1`
  - `subsample=0.8`, `colsample_bytree=0.8`
  - `eval_metric='logloss'`
  - `use_label_encoder=False`

#### 5. 모델 평가
- 정확도: `accuracy_score`
- 분류 리포트: `classification_report`
- 혼동 행렬: `confusion_matrix`

---

## 전체 요약

| 항목   | 내용 |
|--------|------|
| 목적   | 축구 경기의 홈팀 승리 여부 예측 |
| 입력   | Elo, 최근 경기 폼, 예상 득점(xG), 사전 확률, 날짜 등 |
| 타겟   | `result == 2` → 1 (홈승), 그 외 → 0 |
| 모델   | XGBoost (이진 분류) |
| 평가   | Accuracy, Classification Report, Confusion Matrix |

