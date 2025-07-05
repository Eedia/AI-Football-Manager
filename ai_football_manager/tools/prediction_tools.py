import warnings
import logging
warnings.filterwarnings('ignore')
logging.getLogger().setLevel(logging.ERROR)

# soccerdata 로그 차단
logging.getLogger('soccerdata').disabled = True
logging.getLogger('understat').disabled = True

import sys
import os

# tools 폴더의 모듈들을 import하기 위한 경로 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def get_match_prediction(user_input: str):
    """
    사용자 입력을 받아 경기 예측을 수행하는 함수
    
    사용자의 입력을 통해 경기 정보를 추출하고, 해당 정보를 바탕으로 머신러닝 모델을 이용하여 승부 예측을 수행.
    
    Parameters
    ----------
    user_input : str
        사용자가 입력한 경기 예측 요청 문장
        
    Returns
    -------
    dict or None
        예측 결과 딕셔너리 또는 실패 시 None
    """
    try:
        from data_collector_tools import DataCollector
        from match_parser import extract_match_parameters
        from model_predictor import predict_match_result
        
        # 1. 사용자 입력에서 경기 정보 추출
        params = extract_match_parameters(user_input)
        # print(f"[DEBUG] 추출된 파라미터: {params}")
        
        # 파라미터 검증
        if not params["match_date"] or not params["home_team"] or not params["away_team"]:
            return None
        
        # 2. 데이터 수집
        # print(f"[DEBUG] 데이터 수집 시작: {params['match_date']} - {params['home_team']} vs {params['away_team']}")
        collector = DataCollector()
        df_final = collector.collect_features(
            match_date=params["match_date"],
            home_team=params["home_team"],
            away_team=params["away_team"]
        )

        # print(f"[DEBUG] 수집된 데이터: {df_final}")
        df_final.to_csv("collected_features.csv", index=False)  # 디버깅용 CSV 저장
        # 4. 모델 예측
        result_df = predict_match_result(df_final)
        
        if result_df is None or result_df.empty:
            return None
            
        # DataFrame을 딕셔너리로 변환하여 반환
        result_dict = result_df.iloc[0].to_dict()
        
        # print(f"[DEBUG] 예측 결과: {result_dict}")

        return result_dict
        
    except Exception as e:
        print(f"예측 중 오류 발생: {e}")
        return None