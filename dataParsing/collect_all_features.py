def collect_all_features_from_input(user_input: str):
    """
    사용자 입력(한글 문장)만으로 모든 경기 feature 수집 및 xG 병합 완료된 DataFrame 반환.

    고정값:
        - seasons: [2024]
        - save_path: 'teamData_xG.csv'

    Parameters:
        user_input (str): 예시 - "5월 25일 울버햄튼과 브렌트포드 경기"

    Returns:
        pd.DataFrame: 단일 row로 구성된 예측용 feature 데이터
    """
    from dataCollector import DataCollector
    from match_parser import extract_match_parameters
    from merge_understat_xg import merge_understat_xg

    params = extract_match_parameters(user_input)

    collector = DataCollector()
    df = collector.collect_features(
        match_date=params["match_date"],
        home_team=params["home_team"],
        away_team=params["away_team"]
    )

    df = merge_understat_xg(
        df=df,
        seasons=[2024],
        save_path="teamData_xG.csv"
    )

    return df
