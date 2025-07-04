import pandas as pd
from soccerdata import Understat
from typing import List, Optional

def merge_understat_xg(
    df: pd.DataFrame,
    seasons: List[int] = [2021, 2022, 2023, 2024],
    league: str = "ENG-Premier League",
    save_path: Optional[str] = None
) -> pd.DataFrame:
    """
    기존 DataFrame과 Understat xG 데이터를 병합하고 파생 변수 생성.

    Parameters:
        df (pd.DataFrame): 기존 경기 데이터프레임 (MatchDate, HomeTeam, AwayTeam 포함)
        seasons (List[int]): 가져올 시즌 목록
        league (str): Understat에서 사용할 리그 코드
        save_path (Optional[str]): 저장할 경로 (None이면 저장하지 않음)

    Returns:
        pd.DataFrame: xG 데이터가 병합된 결과
    """
    # 1. Understat xG 데이터 로드
    understat = Understat(leagues=league, seasons=seasons)
    xg_df = understat.read_team_match_stats()
    xg_df = xg_df[['date', 'home_team', 'away_team', 'home_xg', 'away_xg']]
    xg_df = xg_df.rename(columns={
        'date': 'MatchDate',
        'home_team': 'HomeTeam',
        'away_team': 'AwayTeam',
        'home_xg': 'h_xg',
        'away_xg': 'a_xg'
    })
    xg_df['MatchDate'] = pd.to_datetime(xg_df['MatchDate']).dt.date

    # 2. 입력 데이터 전처리
    df = df.copy()
    df['MatchDate'] = pd.to_datetime(df['MatchDate']).dt.date

    for col in ['h_xg', 'a_xg']:
        if col not in df.columns:
            df[col] = None

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

    # 3. 병합
    df = pd.merge(df, xg_df, on=['MatchDate', 'HomeTeam', 'AwayTeam'], how='left')

    # 4. 새 xG로 덮어쓰기
    df['h_xg'] = df['h_xg_y']
    df['a_xg'] = df['a_xg_y']

    # 5. 파생 변수
    df['xG_diff'] = df['h_xg'] - df['a_xg']
    df['xg_margin'] = df['xG_diff'].abs()
    df['xg_ratio'] = df['h_xg'] / (df['a_xg'] + 1e-6)

    df = df.sort_values('MatchDate')
    df['rolling_xg_home_5'] = df.groupby('HomeTeam')['h_xg'].transform(lambda x: x.rolling(5, min_periods=1).mean())
    df['rolling_xg_away_5'] = df.groupby('AwayTeam')['a_xg'].transform(lambda x: x.rolling(5, min_periods=1).mean())

    # 6. 불필요한 컬럼 제거
    df.drop(columns=['h_xg_x', 'a_xg_x', 'h_xg_y', 'a_xg_y'], errors='ignore', inplace=True)

    # 7. 저장
    if save_path:
        df.to_csv(save_path, index=False)
        print(f"✅ 저장 완료: {save_path} (행 수: {len(df)})")

    return df
