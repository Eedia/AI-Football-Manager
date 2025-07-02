import pandas as pd
from soccerdata import FotMob

def collect_cleaned_xg_sample():
    fm = FotMob(leagues=["ENG-Premier League"], seasons=["2024"])

    # 1. xG 데이터 (MultiIndex DataFrame)
    df_xg = fm.read_team_match_stats(stat_type="Expected goals (xG)", opponent_stats=True)
    df_xg = df_xg.reset_index()  # league, season, game, team → 컬럼으로 풀기

    # 주요 xG 정보만 선택
    df_xg = df_xg[['league', 'season', 'game', 'team', 'Expected goals (xG)']]

    # 2. 일정 데이터에서 날짜 및 상대 정보 추출
    df_sched = fm.read_schedule().reset_index()
    df_sched = df_sched[['season', 'game', 'date', 'home_team', 'away_team']]

    # 날짜 처리
    df_sched['date'] = pd.to_datetime(df_sched['date']).dt.date

    # 3. 홈팀 기준 merge
    df = df_xg.merge(df_sched, on=['season', 'game'], how='left')

    # 4. venue/opponent 정의
    df['venue'] = df.apply(lambda r: 'home' if r['team'] == r['home_team'] else 'away', axis=1)
    df['opponent'] = df.apply(lambda r: r['away_team'] if r['team'] == r['home_team'] else r['home_team'], axis=1)

    # 5. 컬럼 정리 및 샘플 출력
    df = df.rename(columns={'Expected goals (xG)': 'xG_for'})
    df = df[['date', 'team', 'opponent', 'venue', 'xG_for']]

    print(df)
    df.to_csv("epl_2024_xg_cleaned_sample.csv", index=False)
    return df

import pandas as pd

def add_xg_against_and_diff(csv_path="epl_2024_xg_cleaned_sample.csv"):
    # 1. 기존 xG 데이터 불러오기
    df = pd.read_csv(csv_path)

    # 2. xG_against를 위해 복제 테이블 생성 (team/opponent 위치 바꾸기)
    df_against = df.rename(columns={
        'team': 'opponent',
        'opponent': 'team',
        'xG_for': 'xG_against'
    })[['date', 'team', 'opponent', 'xG_against']]

    # 3. 원본과 병합 (팀+상대+날짜 기준)
    df_merged = df.merge(df_against, on=['date', 'team', 'opponent'], how='left')

    # 4. xG 차이 피처 생성
    df_merged['xG_diff'] = df_merged['xG_for'] - df_merged['xG_against']

    # 5. 저장 및 출력
    df_merged.to_csv("epl_2024_xg_with_diff.csv", index=False)
    print(df_merged.head(10))

    return df_merged

if __name__ == "__main__":
    collect_cleaned_xg_sample()
    add_xg_against_and_diff()
