import joblib
import pandas as pd
from get_model_input import get_model_input  # 경로 확인
from datetime import datetime

# ▶ 사용자 입력
home_team = "Liverpool"
away_team = "Everton"
match_date = "2024-10-26"

# ▶ 날짜 모드 판단 (복기 or 예측)
match_date_parsed = pd.to_datetime(match_date).date()
today = datetime.today().date()
mode = "예측" if match_date_parsed >= today else "복기"
print(f"📅 날짜: {match_date_parsed} ({mode} 모드)")

# ▶ 모델 로드
model = joblib.load("model/model_final.pkl")

# ▶ 피처 생성
feature_order = model.feature_names_in_.tolist()
features = get_model_input(home_team, away_team, match_date)

# 모델에 맞게 입력값 포맷 생성
sample = pd.DataFrame(
    [[features[feat] for feat in feature_order]],
    columns=feature_order
).fillna(0)

# ▶ 예측
prediction = model.predict(sample)[0]
probs = model.predict_proba(sample)[0]

# ▶ 출력
print(f"\n🎯 예측 결과: {'홈승' if prediction == 1 else '무/원정승'}")
print("📊 예측 확률:")
print(f"   홈승: {probs[1]:.2%}")
print(f"   무/원정승: {probs[0]:.2%}")

# ▶ 디버깅용 Feature 출력
print("\n[DEBUG] Feature 결과:")
for k, v in features.items():
    print(f"{k}: {v}")

