import pandas as pd
from soccerdata import Understat

def data_collector(df) -> pd.DataFrame:
    """
    EPL 2015~2025 시즌의 팀별 경기 통계 데이터를 수집하고, 홈·원정 롤링 스탯을 계산하여 반환
    
    Returns
    -------
    pd.DataFrame
        팀별 경기 통계와 롤링 스탯이 포함된 DataFrame
    """

    # 0) EPL 2015~2025 경기 로드  
    LEAGUE  = ["ENG-Premier League"]
    SEASONS = range(2024, 2026)

    us = Understat(leagues=LEAGUE, seasons=SEASONS)
    m = us.read_team_match_stats()[[
        'game_id', 'date',
        'home_team', 'away_team',
        'home_goals', 'away_goals',
        'home_xg',    'away_xg',
        'home_points','away_points'
    ]]
    m['date'] = pd.to_datetime(m['date'])

    # 1) 홈·원정 → long 포맷으로 변환
    home = m.assign(
        team   = m['home_team'],
        goals  = m['home_goals'],
        GA     = m['away_goals'],        # ← 상대 득점 = 내 실점
        xg     = m['home_xg'],
        points = m['home_points'],
        side   = 'home'
    )[['game_id','date','team','side','goals','GA', 'xg','points']]

    away = m.assign(
        team   = m['away_team'],
        goals  = m['away_goals'],
        GA     = m['home_goals'],        # ← 상대(홈) 득점
        xg     = m['away_xg'],
        points = m['away_points'],
        side   = 'away'
    )[['game_id','date','team','side','goals','GA', 'xg','points']]

    long_df = pd.concat([home, away], ignore_index=True)



    # 2) 팀별 롤링 (최근 3·5 경기) + 최신 xG 추출
    def add_rolling(g):
        g = g.sort_values('date', ascending=False)
        for w in (3, 5):
            g[f'GF{w}']    = g['goals'].rolling(w, min_periods=1).sum().shift(1)    # 득점
            g[f'GA{w}']   = g['GA'].rolling(w, min_periods=1).sum().shift(1)        # 실점
            g[f'Form{w}']  = g['points'].rolling(w, min_periods=1).sum().shift(1)   # 점수
        g['rolling_xg_5'] = g['xg'].rolling(5, min_periods=1).mean()

        # 가장 최근 경기의 xg
        g['current_xg'] = g['xg']
        return g

    long_roll = (
        long_df
        .groupby('team', group_keys=False)
        .apply(add_rolling)
    )

    # ────────────────────────────────────────────────
    # 3) 다시 홈·원정 wide 포맷
    # ────────────────────────────────────────────────
    cols_keep = ['game_id','date']
    home_cols = ['rolling_xg_5','Form3','Form5','GF3','GF5','GA3','GA5', 'current_xg']
    away_cols = home_cols            # 이름은 동일, 접두사 달라짐

    home_w = (
        long_roll[long_roll['side'] == 'home']
        .loc[:, cols_keep + ['team'] + home_cols]
        .rename(columns={
            'team': 'HomeTeam',                          # 팀 이름 복사
            **{c: f'home_{c}' for c in home_cols}
        })
    )

    away_w = (
        long_roll[long_roll['side'] == 'away']
        .loc[:, cols_keep + ['team'] + away_cols]
        .rename(columns={
            'team': 'AwayTeam',
            **{c: f'away_{c}' for c in away_cols}
        })
    )

    feat_df = home_w.merge(away_w, on=['game_id', 'date'], how='inner')

    # ─────────────────────────────────────────
    # 4) 컬럼 이름 일괄 매핑
    # ─────────────────────────────────────────
    rename_map = {}

    for base in ['Form3','Form5','GF3','GF5','GA3','GA5']:   
        rename_map[f'home_{base}'] = f'{base}Home'
        rename_map[f'away_{base}'] = f'{base}Away'

    rename_map.update({
        'date' : 'MatchDate',
        'home_rolling_xg_5': 'rolling_xg_home_5',
        'away_rolling_xg_5': 'rolling_xg_away_5',
        'home_current_xg'  : 'h_xg',
        'away_current_xg'  : 'a_xg'
    })

    feat_df = feat_df.rename(columns=rename_map)

    # 원하는 순서로 컬럼 재배치
    cols = [
        'game_id','MatchDate','HomeTeam','AwayTeam',         
        'rolling_xg_home_5','rolling_xg_away_5',
        'Form3Home','Form5Home','Form3Away','Form5Away',
        'GF3Home','GF5Home','GF3Away','GF5Away',
        'GA3Home','GA5Home','GA3Away','GA5Away',
        'h_xg','a_xg'
    ]

    # 컬럼 재배치
    feat_df = feat_df[cols]

    feat_df["MatchDate"] = feat_df["MatchDate"].dt.date
    # 결측치 처리
    feat_df.fillna(0)

    # 5. 파생 변수
    feat_df['xG_diff'] = feat_df['h_xg'] - feat_df['a_xg']
    feat_df['xg_margin'] = feat_df['xG_diff'].abs()
    feat_df['xg_ratio'] = feat_df['h_xg'] / (feat_df['a_xg'] + 1e-6)

    team_name_map = {
        'Man United': 'Manchester United',
        'Tottenham': 'Tottenham',
        'Spurs': 'Tottenham',
        'Wolves': 'Wolverhampton Wanderers',
        'Leeds': 'Leeds United',
        'Newcastle': 'Newcastle United',
        'Nottm Forest': 'Nottingham Forest',
        'Brighton': 'Brighton',
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

    feat_df['HomeTeam'] = feat_df['HomeTeam'].replace(team_name_map)
    feat_df['AwayTeam'] = feat_df['AwayTeam'].replace(team_name_map)

    df_1 = pd.merge(df, feat_df, on=['MatchDate', 'HomeTeam', 'AwayTeam'], how='left')
    return df_1