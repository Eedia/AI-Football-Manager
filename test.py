from soccerdata import FotMob

def inspect_fotmob_columns():
    fm = FotMob(leagues=["ENG-Premier League"], seasons=["2022-23"])

    # xG 관련 팀별 경기 통계 가져오기
    df_team = fm.read_team_match_stats(stat_type="Expected goals (xG)", opponent_stats=True)
    print("📘 read_team_match_stats() columns:")
    print(df_team.columns.tolist())
    print(df_team.head(2))

    # 전체 경기 통계 (xG 포함, 날짜 등)
    df_match = fm.read_team_match_stats(stat_type="Expected goals (xG)", opponent_stats=True)
    print("\n📗 read_match_stats() columns:")
    print(df_match.columns.tolist())
    print(df_match.head(2))

    # 경기 일정
    df_sched = fm.read_schedule()
    print("\n📙 read_schedule() columns:")
    print(df_sched.columns.tolist())
    print(df_sched.head(2))

if __name__ == "__main__":
    inspect_fotmob_columns()
