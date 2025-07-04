import numpy as np
import pandas as pd
import joblib
import os

# 모델 로딩 (최초 1회)
# 이 코드와 model_predictor.py는 동일한 디렉토리에 있어야 함
_model = None
_model_path = os.path.join(os.path.dirname(__file__), "model_final.pkl")

log_columns = ['HomeElo', 'AwayElo']

def load_model():
    global _model
    if _model is None:
        _model = joblib.load(_model_path)
    return _model

def predict_match_result(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    학습된 모델을 이용해 경기 정보를 받아 승부 예측 결과를 반환

    Parameters
    ----------
    df_input : pd.DataFrame
        예측에 필요한 feature 컬럼 포함된 경기 데이터

    Returns
    -------
    pd.DataFrame
        예측 결과가 포함된 DataFrame
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
