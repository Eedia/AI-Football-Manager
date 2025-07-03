# 축구 경기 승패 예측 모델 요약

## 1. 데이터셋 요약 (`EPL_2019_2025.csv`)

### 목적
- 축구 경기의 승패 예측, **홈팀 승리 여부**를 예측하는 데 사용되는 데이터셋

### 구조
- 행(row): 각 경기
- 열(column): 경기 정보, 팀 전력, 폼, xG, 베팅 확률 등

### 주요 피처 그룹

| 컬럼명                    | 설명                                                              | 예측에 사용 여부 |
| ------------------------ | ----------------------------------------------------------------- | --------------- |
| **MatchDate**            | 경기 날짜 (예: `2000-07-28`)                                      |  |
| **HomeTeam**             | 홈 팀 이름                                                        |  |
| **AwayTeam**             | 원정 팀 이름                                                      |  |
| **HomeElo**              | 경기 시점에서의 홈 팀 Elo 점수 (실력 지표)                          | ✅ |
| **AwayElo**              | 경기 시점에서의 원정 팀 Elo 점수                                   | ✅ |
| **elo\_diff**            | 홈 팀과 원정 팀의 Elo 점수 차이 (HomeElo - AwayElo)                | ✅ |
| **Form3Home**            | 홈 팀의 최근 3경기 폼                                              | ✅ |
| **Form5Home**            | 홈 팀의 최근 5경기 폼                                             | ✅ |
| **Form3Away**            | 원정 팀의 최근 3경기 폼                                           | ✅ |
| **Form5Away**            | 원정 팀의 최근 5경기 폼                                           | ✅ |
| **h\_xg**                | 홈 팀의 기대 득점 (Expected Goals)                               | ✅ |
| **a\_xg**                | 원정 팀의 기대 득점                                              | ✅ |
| **xG\_diff**             | 홈 팀 기대 득점 - 원정 팀 기대 득점 (`h_xg - a_xg`)               | ✅ |
| **xg\_margin**           | 절댓값 기반의 xG 차이 (예: `abs(h_xg - a_xg)`)                    | ✅ |
| **xg\_ratio**            | 홈 팀 기대 득점 비율 (`h_xg / (h_xg + a_xg)`), 두 팀의 전체 기대 득점 중 홈 팀의 비율 | ✅ |
| **result**               | 실제 경기 결과 (0 = 무승부, 1 = 원정 승, 2 = 홈 승 등으로 추정)    | |
| **rolling\_xg\_home\_5** | 홈 팀의 최근 5경기 평균 xG (롤링 평균)                            | ✅ |
| **elo\_change\_home**    | 직전 경기 이후 홈 팀의 Elo 점수 변화량                            | ✅ |
| **rolling\_xg\_away\_5** | 원정 팀의 최근 5경기 평균 xG (롤링 평균)                          | ✅ |
| **elo\_change\_away**    | 직전 경기 이후 원정 팀의 Elo 점수 변화량                          | ✅ |


> 시즌 초 경기에는 xG, 폼 등 결측치가 다수 존재

## 2. 모델 코드 요약 (`xgb_model.pkl`)

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

```text
🎯 Accuracy: 0.7378640776699029

📋 Classification Report:
               precision    recall  f1-score   support

           0       0.78      0.77      0.78       122
           1       0.67      0.69      0.68        84

    accuracy                           0.74       206
   macro avg       0.73      0.73      0.73       206
weighted avg       0.74      0.74      0.74       206


🧱 Confusion Matrix:
 [[94 28]
 [26 58]]
```

### 예측 모델 요약

| 항목   | 내용 |
|--------|------|
| 목적   | 축구 경기의 홈팀 승리 여부 예측 |
| 입력   | Elo, 최근 경기 폼, 예상 득점(xG), 사전 확률, 날짜 등 |
| 타겟   | `result == 2` → 1 (홈승), 그 외 → 0 |
| 모델   | XGBoost (이진 분류) |
| 평가   | Accuracy, Classification Report, Confusion Matrix |

## 3. 예측 결과 출력 함수 요약 (`predict.py`)

### 목적
- 두 축구 팀의 경기 결과를 머신러닝 모델(XGBoost)을 통해 예측
- 입력된 날짜를 기준으로 **예측 모드** 또는 **복기(검증) 모드**로 전환

### 사용 모델
- 저장된 모델 파일: `xgb_model.pkl`
- 입력 피처는 `get_model_input()` 함수를 통해 자동 생성 → soccerdata를 통해 가져옴
- 예측 대상: 홈팀이 이길 확률 (이진 분류, 1: 홈승 / 0: 무승부 또는 원정승)

### 입력값 설명
- `home_team`: 홈팀 이름 (Understat 및 Elo 기준 정확히 일치해야 함)
- `away_team`: 원정팀 이름
- `match_date`: 경기 날짜 (`"YYYY-MM-DD"` 형식)
  - 오늘보다 미래면 **예측 모드**
  - 과거면 **복기 모드**

#### 입력 예시

``` text
home_team = "Liverpool"     # 홈팀 이름
away_team = "Everton"       # 원정팀 이름
match_date = "2024-10-26"   # 경기 날짜 (예측 기준일)
```

### 코드 동작 흐름

1. **모드 판별**
   - 오늘 날짜와 비교하여 예측/복기 모드 결정
   - 출력 예: `📅 날짜: 2024-10-26 (예측 모드)`

2. **모델 로드 및 입력 생성**
   - `joblib.load("xgb_model.pkl")`로 모델 로드
   - `get_model_input()`으로 21개 특징(feature) 생성
   - 모델 학습에 사용된 순서대로 `DataFrame` 구성

3. **예측 및 확률 출력**
   - `model.predict()`로 홈팀 승리 여부 예측
   - `model.predict_proba()`로 홈승 확률과 무/원정승 확률 출력

#### 출력 예시

``` text
📅 날짜: 2024-10-26 (예측 모드)

🎯 예측 결과: 무/원정승
📊 예측 확률:
홈승: 31.77%
무/원정승: 68.23%
```

### 주의사항
- `get_model_input()`의 일부 피처(`prob_home`, `prob_draw`, `prob_away`)는 현재 `NaN`으로 설정되어 있으며 향후 API 연동 시 보완 예정 → 삭제
- 입력 팀 이름은 정확하게 일치해야 하며, 오탈자 또는 약칭 사용 시 오류 발생 가능
- `NaN` 값은 0으로 자동 대체하여 예측에 사용됨

### 활용 팁
- 복기 모드로 시연 시 실제 경기 결과와 비교하여 모델의 정확도 강조 가능
- 예측 모드로 사용 시 당일 경기 또는 미래 경기의 승패 예측에 활용 가능
