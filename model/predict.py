import joblib
import pandas as pd
from model.get_model_input import get_model_input

# 사용자 입력
home_team = "Liverpool"
away_team = "Everton"
match_date = "2024-11-26"

# 모델 로드
model = joblib.load("xgb_model_1.pkl")

# 학습에 사용된 피처 순서
feature_order = model.feature_names_in_.tolist()

# 모델 입력 피처 생성
features = get_model_input(home_team, away_team, match_date)

# 정확한 순서로 입력 데이터 생성
sample = pd.DataFrame([[features[feat] for feat in feature_order]], columns=feature_order).fillna(0)

# 예측
prediction = model.predict(sample)[0]
probability = model.predict_proba(sample)[0][1]

# 출력
print(f"🎯 예측 결과: {'홈승' if prediction == 1 else '무/원정승'}")
print(f"📊 예측 확률 (홈승): {probability:.2%}")