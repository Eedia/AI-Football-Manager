import joblib
import pandas as pd
from get_model_input import get_model_input
from datetime import datetime

# 사용자 입력
home_team = "Everton"
away_team = "Liverpool"
match_date = "2024-11-26"                               # 예시 날짜, 실제로는 사용자 입력으로 받거나 자동으로 설정
# match_date = datetime.today().strftime("%Y-%m-%d")    # 오늘 날짜로 예측하는 경우

# 날짜 파싱 및 모드 구분
match_date_parsed = pd.to_datetime(match_date).date()
today = datetime.today().date()
mode = "예측" if match_date_parsed >= today else "복기"
print(f"📅 날짜: {match_date_parsed} ({mode} 모드)")

# 모델 로드
model = joblib.load("xgb_model.pkl")
feature_order = model.feature_names_in_.tolist()

# 모델 입력 피처 생성
features = get_model_input(home_team, away_team, match_date)
sample = pd.DataFrame([[features[feat] for feat in feature_order]], columns=feature_order).fillna(0)

# 예측
prediction = model.predict(sample)[0]
probs = model.predict_proba(sample)[0]

# 출력
print(f"\n🎯 예측 결과: {'홈승' if prediction == 1 else '무/원정승'}")
print("📊 예측 확률:")
print(f"   홈승: {probs[1]:.2%}")
print(f"   무/원정승: {probs[0]:.2%}")