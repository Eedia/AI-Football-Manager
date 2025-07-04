def predict(user_input: str):
    """
    이 함수만 호출하면 데이터 수집 및 예측 까지 실시
    
    사용자의 입력을 받아 경기 정보를 추출하고,
    해당 정보를 기반으로 모든 feature를 수집하여 예측 결과를 반환

    RE : 
        예측 결과가 포함된 DataFrame
    """
    from dataCollector import DataCollector
    from match_parser import extract_match_parameters
    from model_predictor import predict_match_result

    params = extract_match_parameters(user_input)

    collector = DataCollector()
    
    df = collector.collect_features(
        match_date=params["match_date"],
        home_team=params["home_team"],
        away_team=params["away_team"]
    )

    df_final = collector.data_collector(df)
    
    result = predict_match_result(df_final)

    return result
