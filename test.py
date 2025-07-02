import pandas as pd
import soccerdata as sd
from soccerdata import ClubElo
from datetime import timedelta

def collect_understat_data():
    us = sd.Understat(leagues=["ENG-Premier League"], seasons=["2022-23"])
    # 팀별 xG 포함 매치 통계 수집
    df = us.read_team_match_stats()  # 팀 기준 매치 데이터
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df

def collect_elo(start_date, end_date):
    elo = ClubElo()
    all_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    dfs = []

    for d in all_dates:
        try:
            daily_df = elo.read_by_date(d)
            daily_df['date'] = d.date()
            dfs.append(daily_df)
        except Exception:
            continue  # Elo 데이터가 없는 날은 패스

    return pd.concat(dfs, ignore_index=True)

def merge_data(df, elo_df):
    df = df.rename(columns={
        'team': 'h_team', 'opponent': 'a_team',
        'xG_for': 'h_xg', 'xG_against': 'a_xg',
        'goals_for': 'h_goals', 'goals_against': 'a_goals'
    })
    df = df.merge(elo_df.rename(columns={'team':'h_team','elo':'h_elo'}), on=['date','h_team'], how='left')
    df = df.merge(elo_df.rename(columns={'team':'a_team','elo':'a_elo'}), on=['date','a_team'], how='left')
    df['result'] = df.apply(lambda r: 2 if r.h_goals>r.a_goals else (1 if r.h_goals==r.a_goals else 0), axis=1)
    return df

def main():
    df = collect_understat_data()
    elo_df = collect_elo(df['date'].min(), df['date'].max())
    merged = merge_data(df, elo_df)
    merged.to_csv('processed/epl_2022.csv', index=False)
    print(merged.head())

if __name__=='__main__':
    main()
