import pandas as pd
from soccerdata import FotMob

def make_final_match_dataset():
    # 1. xG 데이터 로드
    df = pd.read_csv("epl_2024_xg_with_diff.csv")
    df = df.loc[:, ~df.columns.duplicated()]

    # 2. 홈/어웨이 분리
    df_home = df[df["venue"] == "home"].copy()
    df_away = df[df["venue"] == "away"].copy()

    # 3. 홈-어웨이 병합
    merged = df_home.merge(
        df_away,
        left_on=["date", "team", "opponent"],
        right_on=["date", "opponent", "team"],
        suffixes=("_h", "_a")
    )

    # 4. FotMob 일정 로드
    fm = FotMob(leagues=["ENG-Premier League"], seasons=["2024-25"])
    sched = fm.read_schedule().reset_index()
    sched["date"] = pd.to_datetime(sched["date"]).dt.date

    sched = sched.rename(columns={
        "home_team": "team_h",
        "away_team": "team_a",
        "home_score": "h_goals",
        "away_score": "a_goals"
    })
    sched = sched[["season", "date", "team_h", "team_a", "h_goals", "a_goals"]]

    # 5. 병합을 위한 컬럼 정리
    merged = merged.rename(columns={
        "team_h": "team_h",
        "opponent_h": "team_away",
        "xG_for_h": "h_xg",
        "xG_for_a": "a_xg"
    })
    merged["xG_diff"] = (merged["h_xg"] - merged["a_xg"]).round(2)
    merged["date"] = pd.to_datetime(merged["date"]).dt.date

    # 6. 병합 (충돌 방지 위해 team_away 사용)
    final = merged.merge(sched, left_on=["date", "team_h", "team_away"], right_on=["date", "team_h", "team_a"], how="left")

    # 7. 병합 후 정리: team_away → team_a
    final = final.rename(columns={"team_away": "team_a"})

    # 8. result 계산
    def get_result(row):
        if pd.isna(row["h_goals"]) or pd.isna(row["a_goals"]):
            return None
        if row["h_goals"] > row["a_goals"]:
            return 2
        elif row["h_goals"] < row["a_goals"]:
            return 0
        else:
            return 1

    final["result"] = final.apply(get_result, axis=1)

    # 9. 최종 컬럼 순서
    final = final[[
        "season", "date", "team_h", "team_a",
        "h_goals", "a_goals", "h_xg", "a_xg", "xG_diff", "result"
    ]]

    # 10. 후처리: season 포맷, goal 공백 정리
    final["season"] = final["season"].astype(str)
    final["season"] = final["season"].apply(lambda s: f"20{s[:2]}-{s[2:]}")

    final["h_goals"] = final["h_goals"].astype(str).str.strip().astype(int)
    final["a_goals"] = final["a_goals"].astype(str).str.strip().astype(int)


    final.to_csv("epl_2024_match_data_final.csv", index=False)
    print("✅ 저장 완료: epl_2024_match_data_final.csv")
    print(final.head())

if __name__ == "__main__":
    make_final_match_dataset()
