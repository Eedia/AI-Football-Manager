# 축구 경기 승패 예측 모델 요약

## 1. 데이터셋 요약 (`EPL_2000_2025.csv`)

### 목적
- 축구 경기의 승패 예측, **홈팀 승리 여부**를 예측하는 데 사용되는 데이터셋

### 구조
- 행(row): 각 경기
- 열(column): 경기 정보, 팀 전력, 폼, xG, 베팅 확률 등

### 주요 피처 그룹

| 컬럼명                    | 설명                                                              |
| ------------------------ | ---------------------------------------------------------------- |
| **MatchDate**            | 경기 날짜 (예: `2000-07-28`)                                      |
| **HomeTeam**             | 홈 팀 이름                                                        |
| **AwayTeam**             | 원정 팀 이름                                                      |
| **HomeElo**              | 경기 시점에서의 홈 팀 Elo 점수 (실력 지표)                          |
| **AwayElo**              | 경기 시점에서의 원정 팀 Elo 점수                                   |
| **elo\_diff**            | 홈 팀과 원정 팀의 Elo 점수 차이 (HomeElo - AwayElo)                |
| **Form3Home**            | 홈 팀의 최근 3경기 폼                                              |
| **Form5Home**            | 홈 팀의 최근 5경기 폼                                             |
| **Form3Away**            | 원정 팀의 최근 3경기 폼                                           |
| **Form5Away**            | 원정 팀의 최근 5경기 폼                                           |
| **prob\_home**           | 경기 전 예측된 홈 팀 승리 확률                                     |
| **prob\_draw**           | 무승부 확률                                                      |
| **prob\_away**           | 원정 팀 승리 확률                                                |
| **h\_xg**                | 홈 팀의 기대 득점 (Expected Goals)                               |
| **a\_xg**                | 원정 팀의 기대 득점                                              |
| **xG\_diff**             | 홈 팀 기대 득점 - 원정 팀 기대 득점 (`h_xg - a_xg`)               |
| **xg\_margin**           | 절댓값 기반의 xG 차이 (예: `abs(h_xg - a_xg)`)                    |
| **xg\_ratio**            | 홈 팀 기대 득점 비율 (`h_xg / (h_xg + a_xg)`), 두 팀의 전체 기대 득점 중 홈 팀의 비율 |
| **month**                | 경기 월 (숫자, 예: `7` = 7월)                                    |
| **weekday**              | 요일 (숫자: 월=0, 화=1, …, 일=6 또는 어떤 기준인지 확인 필요)      |
| **result**               | 실제 경기 결과 (0 = 무승부, 1 = 원정 승, 2 = 홈 승 등으로 추정)    |
| **rolling\_xg\_home\_5** | 홈 팀의 최근 5경기 평균 xG (롤링 평균)                            |
| **elo\_change\_home**    | 직전 경기 이후 홈 팀의 Elo 점수 변화량                            |
| **rolling\_xg\_away\_5** | 원정 팀의 최근 5경기 평균 xG (롤링 평균)                          |
| **elo\_change\_away**    | 직전 경기 이후 원정 팀의 Elo 점수 변화량                          |


> 시즌 초 경기에는 xG, 폼 등 결측치가 다수 존재

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

#### 5. 모델 평가 결과

🎯 **Accuracy**: 0.7384615384615385

📋 **Classification Report**:
               precision    recall  f1-score   support

           0       0.71      0.78      0.74        63
           1       0.77      0.70      0.73        67

    accuracy                           0.74       130
   macro avg       0.74      0.74      0.74       130
weighted avg       0.74      0.74      0.74       130


🧱 **Confusion Matrix**:
 [[49 14]
 [20 47]]

## 전체 요약

| 항목   | 내용 |
|--------|------|
| 목적   | 축구 경기의 홈팀 승리 여부 예측 |
| 입력   | Elo, 최근 경기 폼, 예상 득점(xG), 사전 확률, 날짜 등 |
| 타겟   | `result == 2` → 1 (홈승), 그 외 → 0 |
| 모델   | XGBoost (이진 분류) |
| 평가   | Accuracy, Classification Report, Confusion Matrix |

