import numpy as np
import pandas as pd
import joblib
import os

# 모델 파일 경로를 프로젝트 루트 기준으로 설정
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # tools/ 상위 폴더 (프로젝트 루트)
MODEL_PATH = os.path.join(PROJECT_ROOT, "models", "model_final.pkl")

_model = None
log_columns = ['HomeElo', 'AwayElo']

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def predict_match_result(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    학습된 모델을 이용해 경기 정보를 받아 승부 예측 결과를 반환
    """
    df = df_input.copy()

    # 전처리: 로그변환 및 파생 변수
    df[log_columns] = np.log1p(df[log_columns])
    df['elo_diff'] = df['HomeElo'] - df['AwayElo']

    # 예측
    model = load_model()
    proba = model.predict_proba(df)[:, 1]
    pred = (proba > 0.5).astype(int)

    result_df = df_input.copy()
    result_df["AwayWin_Prob"] = proba
    result_df["Pred_Label"] = pred
    result_df["Pred_Result"] = result_df["Pred_Label"].map({0: "Home Win", 1: "Away Win"})

    return result_df
