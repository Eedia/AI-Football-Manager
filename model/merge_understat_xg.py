import pandas as pd
from soccerdata import Understat
from typing import List, Optional

def merge_understat_xg_multi(
    csv_path: str,
    save_path: Optional[str] = None,
    seasons: List[int] = list(range(2000, 2025 + 1)),
    leagues: List[str] = [
        "ENG-Premier League", "ESP-La Liga", "ITA-Serie A",
        "GER-Bundesliga", "FRA-Ligue 1"
    ]
) -> pd.DataFrame:
    """
    여러 리그의 Understat xG 데이터를 기존 CSV와 병합

    Parameters:
        csv_path (str): 기존 경기 CSV 경로
        save_path (Optional[str]): 저장할 경로
        seasons (List[int]): 시즌 리스트
        leagues (List[str]): 수집할 리그들 (예: ["ENG-Premier League", ...])

    Returns:
        pd.DataFrame: 병합된 전체 데이터
    """

    # 1. Understat 데이터 수집
    all_xg_df = []
    for league in leagues:
        understat = Understat(leagues=league, seasons=seasons)
        xg_df = understat.read_team_match_stats()
        xg_df = xg_df[['date', 'home_team', 'away_team', 'home_xg', 'away_xg']]
        xg_df['league'] = league
        all_xg_df.append(xg_df)

    xg_all = pd.concat(all_xg_df, ignore_index=True)
    xg_all = xg_all.rename(columns={
        'date': 'MatchDate',
        'home_team': 'HomeTeam',
        'away_team': 'AwayTeam',
        'home_xg': 'h_xg',
        'away_xg': 'a_xg'
    })
    xg_all['MatchDate'] = pd.to_datetime(xg_all['MatchDate']).dt.date

    # 2. 기존 데이터 로드
    df = pd.read_csv(csv_path)
    df['MatchDate'] = pd.to_datetime(df['MatchDate']).dt.date

    # 3. 팀명 정규화
    team_name_map = {
        'Man United': 'Manchester United',
        'Spurs': 'Tottenham',
        'Wolves': 'Wolverhampton Wanderers',
        'Leeds': 'Leeds United',
        'Newcastle': 'Newcastle United',
        'Nottm Forest': 'Nottingham Forest',
        'Brighton': 'Brighton and Hove Albion',
        'West Brom': 'West Bromwich Albion',
        'Sheff Utd': 'Sheffield United',
        'Norwich': 'Norwich City',
        'Cardiff': 'Cardiff City',
        'Hull': 'Hull City',
        'QPR': 'Queens Park Rangers',
        'Blackpool': 'Blackpool',
        'Stoke': 'Stoke City',
    }
    df['HomeTeam'] = df['HomeTeam'].replace(team_name_map)
    df['AwayTeam'] = df['AwayTeam'].replace(team_name_map)

    # 4. 병합
    df = pd.merge(df, xg_all, on=['MatchDate', 'HomeTeam', 'AwayTeam'], how='left')

    # 5. 파생 변수
    df['xG_diff'] = df['h_xg']
    df['xG_diff'] = df['h_xg'] - df['a_xg']
    df['xg_margin'] = df['xG_diff'].abs()
    df['xg_ratio'] = df['h_xg'] / (df['a_xg'] + 1e-6)

    df = df.sort_values('MatchDate')
    df['rolling_xg_home_5'] = df.groupby('HomeTeam')['h_xg'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df['rolling_xg_away_5'] = df.groupby('AwayTeam')['a_xg'].transform(lambda x: x.rolling(5, min_periods=1).mean())

    # 6. 저장 또는 반환
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"✅ 저장 완료: {save_path} (행 수: {len(df)})")

    return df
