def predict(user_input: str):
    """
    사용자의 입력을 받아 경기 정보를 추출하고,
    해당 정보를 기반으로 모든 feature를 수집하여 예측 결과를 반환

    RE : 
        예측 결과가 포함된 DataFrame
    """
    from dataCollector import DataCollector
    from match_parser import extract_match_parameters
    from data_collector import data_collector
    from model_predictor import predict_match_result

    params = extract_match_parameters(user_input)

    print(params)
    collector = DataCollector()
    df = collector.collect_features(
        match_date=params["match_date"],
        home_team=params["home_team"],
        away_team=params["away_team"]
    )

    df_final = data_collector(df)

    result = predict_match_result(df_final)

    return result
