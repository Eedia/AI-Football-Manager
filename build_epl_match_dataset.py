import pandas as pd
from soccerdata import FotMob

def collect_xg_raw(season: str):
    """xG 데이터 수집 및 전처리"""
    fm = FotMob(leagues=["ENG-Premier League"], seasons=[season])
    df_xg = fm.read_team_match_stats(stat_type="Expected goals (xG)", opponent_stats=True).reset_index()
    df_xg = df_xg[['league', 'season', 'game', 'team', 'Expected goals (xG)']]

    df_sched = fm.read_schedule().reset_index()
    df_sched = df_sched[['season', 'game', 'date', 'home_team', 'away_team']]
    df_sched['date'] = pd.to_datetime(df_sched['date']).dt.date

    df = df_xg.merge(df_sched, on=['season', 'game'], how='left')
    df['venue'] = df.apply(lambda r: 'home' if r['team'] == r['home_team'] else 'away', axis=1)
    df['opponent'] = df.apply(lambda r: r['away_team'] if r['team'] == r['home_team'] else r['home_team'], axis=1)

    df = df.rename(columns={'Expected goals (xG)': 'xG_for'})
    df = df[['date', 'team', 'opponent', 'venue', 'xG_for']]
    df.to_csv(f"epl_{season.replace('-', '')}_xg_cleaned_sample.csv", index=False)
    return df


def add_xg_diff(season: str):
    """xG_against, xG_diff 추가"""
    df = pd.read_csv(f"epl_{season.replace('-', '')}_xg_cleaned_sample.csv")
    df_against = df.rename(columns={
        'team': 'opponent',
        'opponent': 'team',
        'xG_for': 'xG_against'
    })[['date', 'team', 'opponent', 'xG_against']]

    df_merged = df.merge(df_against, on=['date', 'team', 'opponent'], how='left')
    df_merged['xG_diff'] = (df_merged['xG_for'] - df_merged['xG_against']).round(2)
    df_merged.to_csv(f"epl_{season.replace('-', '')}_xg_with_diff.csv", index=False)
    return df_merged


def build_match_dataset(season: str):
    """최종 match dataset 생성 (xG + 실제 득점 + 결과)"""
    df = pd.read_csv(f"epl_{season.replace('-', '')}_xg_with_diff.csv")
    df = df.loc[:, ~df.columns.duplicated()]

    df_home = df[df["venue"] == "home"].copy()
    df_away = df[df["venue"] == "away"].copy()

    merged = df_home.merge(
        df_away,
        left_on=["date", "team", "opponent"],
        right_on=["date", "opponent", "team"],
        suffixes=("_h", "_a")
    )

    fm = FotMob(leagues=["ENG-Premier League"], seasons=[season])
    sched = fm.read_schedule().reset_index()
    sched["date"] = pd.to_datetime(sched["date"]).dt.date

    sched = sched.rename(columns={
        "home_team": "team_h",
        "away_team": "team_a",
        "home_score": "h_goals",
        "away_score": "a_goals"
    })
    sched = sched[["season", "date", "team_h", "team_a", "h_goals", "a_goals"]]

    merged = merged.rename(columns={
        "team_h": "team_h",
        "opponent_h": "team_away",
        "xG_for_h": "h_xg",
        "xG_for_a": "a_xg"
    })
    merged["xG_diff"] = (merged["h_xg"] - merged["a_xg"]).round(2)
    merged["date"] = pd.to_datetime(merged["date"]).dt.date

    final = merged.merge(sched, left_on=["date", "team_h", "team_away"], right_on=["date", "team_h", "team_a"], how="left")
    final = final.rename(columns={"team_away": "team_a"})

    def get_result(row):
        if pd.isna(row["h_goals"]) or pd.isna(row["a_goals"]):
            return None
        if int(row["h_goals"]) > int(row["a_goals"]):
            return 2
        elif int(row["h_goals"]) < int(row["a_goals"]):
            return 0
        else:
            return 1

    final["result"] = final.apply(get_result, axis=1)

    final = final[[
        "season", "date", "team_h", "team_a",
        "h_goals", "a_goals", "h_xg", "a_xg", "xG_diff", "result"
    ]]

    final["season"] = final["season"].astype(str)
    final["season"] = final["season"].apply(lambda s: f"20{s[:2]}-{s[2:]}" if "-" not in s else s)
    final["h_goals"] = final["h_goals"].astype(str).str.strip().astype(int)
    final["a_goals"] = final["a_goals"].astype(str).str.strip().astype(int)

    final.to_csv(f"epl_{season.replace('-', '')}_match_data_final.csv", index=False)
    print(f"✅ 저장 완료: epl_{season.replace('-', '')}_match_data_final.csv")
    print(final.head())
    return final


if __name__ == "__main__":
    # 예: "2023-24" 또는 "2024-25"
    target_season = "2023-24"
    collect_xg_raw(target_season)
    add_xg_diff(target_season)
    build_match_dataset(target_season)
