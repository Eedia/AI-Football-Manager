import streamlit as st
import pickle

# 모델 로드
@st.cache_resource
def load_model():
    with open('model_final.pkl', 'rb') as f:
        return pickle.load(f)

model = load_model()

st.title("⚽ 경기 결과 예측 - XGBoost 모델")

# 입력 받기 (총 6개)
elo_home = st.number_input("홈 팀 Elo", value=1500.0)
elo_away = st.number_input("원정 팀 Elo", value=1500.0)
elo_diff = elo_home - elo_away  # 자동 계산하거나 수동 입력할 수 있음

h_xg = st.number_input("홈 팀 xG", value=1.5)
a_xg = st.number_input("원정 팀 xG", value=1.2)
xg_diff = h_xg - a_xg

# 예측 버튼
if st.button("예측하기"):
    features = [[elo_home, elo_away, elo_diff, h_xg, a_xg, xg_diff]]
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0][1]  # 승리 확률 (1에 대한 확률)
    
    result_text = "홈 팀 승리" if prediction == 1 else "홈 팀 패배 또는 무승부"
    st.write(f"🔮 예측 결과: **{result_text}**")
    st.write(f"📊 승리 확률: **{proba:.2%}**")