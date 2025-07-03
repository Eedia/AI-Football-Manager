"""
이 파일은 사전 학습된 XGBoost 모델(xgb_model.pkl)을 로드하고,
해당 모델에 입력될 feature를 기반으로 '홈팀 승리 여부'를 예측한다.

예측 결과는 이진 분류
    - 1: 홈팀 승리
    - 0: 무승부 또는 원정팀 승리

현재 구조:
- 사용자가 직접 모든 feature(21개)를 입력한 경우에만 작동함
- 실제 서비스에서는 사용자가 팀명만 입력하면, 이 feature들을 자동으로 계산하는 함수가 필요 -> 추후 api를 사용하여 구현할 필요 있음
"""

import joblib
import pandas as pd

# 1. 학습된 모델 로드
model = joblib.load("xgb_model.pkl")


# 2. 예측 함수 정의
def predict_from_features(feature_dict: dict) -> int:
    """
    21개 feature를 입력받아 예측 결과를 반환
    
    Args:
        feature_dict (dict): 모델에 입력할 21개 피처의 값

    Returns:
        int: 예측 결과 (1=홈승, 0=무승부 또는 원정승)
    """
    df = pd.DataFrame([feature_dict])
    pred = model.predict(df)[0]
    return int(pred)


# 3. 예시 입력 및 테스트 실행 (직접 실행 시만 동작)
if __name__ == "__main__":
    # 예측에 사용될 샘플 입력값
    # 실제 서비스에서는 이 값들을 get_model_input() 함수에서 자동으로 생성하게 될 예정
    sample_input = {
        'HomeElo': 1700,
        'AwayElo': 1650,
        'elo_diff': 50,
        'Form3Home': 2.0,
        'Form5Home': 3.5,
        'Form3Away': 1.0,
        'Form5Away': 2.5,
        'prob_home': 0.55,
        'prob_draw': 0.25,
        'prob_away': 0.20,
        'h_xg': 1.7,
        'a_xg': 1.1,
        'xG_diff': 0.6,
        'xg_margin': 0.5,
        'xg_ratio': 0.61,
        'rolling_xg_home_5': 1.5,
        'rolling_xg_away_5': 1.2,
        'elo_change_home': 5,
        'elo_change_away': -3,
        'month': 10,
        'weekday': 6
    }

    result = predict_from_features(sample_input)

    print("예측 결과:", "홈승" if result == 1 else "무승부/원정승")
