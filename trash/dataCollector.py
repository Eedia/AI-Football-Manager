import pandas as pd
import soccerdata as sd

class DataCollector:
    def __init__(self):
        # FBref에서 프리미어리그 2024-25 시즌 데이터를 로드
        self.fbref = sd.FBref(
            leagues="ENG-Premier League",
            seasons="2425",
            no_cache=True
        )
        # ClubElo API 로딩
        self.clubelo = sd.ClubElo()

        # 미리 시즌 경기 일정을 가져와 저장 (재사용 가능)
        self.schedule_df = self.fbref.read_schedule().reset_index()

        # Elo 데이터 캐시: 날짜별, 팀별
        self.elo_by_date_cache = {}
        self.elo_team_history_cache = {}

        # 팀 이름 정규화용 매핑
        self.team_name_map = {
            "Arsenal": "Arsenal", "Aston Villa": "Aston Villa", "Bournemouth": "Bournemouth",
            "Brentford": "Brentford", "Brighton": "Brighton", "Chelsea": "Chelsea",
            "Crystal Palace": "Crystal Palace", "Everton": "Everton", "Fulham": "Fulham",
            "Leeds United": "Leeds United", "Liverpool": "Liverpool", "Man City": "Man City",
            "Man Utd": "Man Utd", "Newcastle": "Newcastle", "Nottingham Forest": "Nottingham Forest",
            "Southampton": "Southampton", "Spurs": "Spurs", "West Ham": "West Ham", "Wolves": "Wolves"
        }

    def get_team_elo(self, team_alias, match_date):
        """
        경기 하루 전의 팀 Elo 레이팅을 반환
        """
        official_name = self.team_name_map.get(team_alias, team_alias)
        match_date = pd.to_datetime(match_date)
        day_before = match_date - pd.Timedelta(days=1)

        # 날짜별 Elo 캐싱 (API 호출 최소화)
        if day_before not in self.elo_by_date_cache:
            try:
                df = self.clubelo.read_by_date(date=day_before).reset_index()
                self.elo_by_date_cache[day_before] = df
            except Exception as e:
                print(f"Elo 데이터 로딩 실패: {e}")
                return None

        df = self.elo_by_date_cache[day_before]
        filtered = df[df["team"].str.lower() == official_name.lower()]
        if filtered.empty:
            print(f"Elo 데이터 없음: {official_name} on {day_before.date()}")
            return None
        return filtered.iloc[0]["elo"]

    def get_team_elo_change(self, team_alias, match_date):
        """
        최근 두 번의 Elo 변화량 (증감)을 계산
        """
        official_name = self.team_name_map.get(team_alias, team_alias)
        match_date = pd.to_datetime(match_date)

        if official_name not in self.elo_team_history_cache:
            try:
                df = self.clubelo.read_team_history(official_name).reset_index()
                df["from"] = pd.to_datetime(df["from"])
                self.elo_team_history_cache[official_name] = df
            except Exception as e:
                print(f"Elo 데이터 로딩 실패: {e}")
                return None

        df = self.elo_team_history_cache[official_name]
        df_before = df[df["from"] < match_date].sort_values("from")

        # Elo 히스토리가 너무 짧을 경우 예외 처리
        if len(df_before) < 2:
            print(f"{official_name} elo가 2개 미만입니다.")
            return 0

        elo_now = df_before.iloc[-1]["elo"]
        elo_prev = df_before.iloc[-2]["elo"]
        return elo_now - elo_prev

    def get_last_n_matches_goal_diff(self, team_name, n, match_date):
        """
        특정 팀의 마지막 n경기 득점/실점/골차 데이터
        """
        sched = self.schedule_df.copy()
        team_lower = team_name.lower()
        sched["date"] = pd.to_datetime(sched["date"])

        # 해당 경기 이전 경기만 필터링
        sched = sched[sched["date"] < match_date]

        # 홈팀 또는 원정팀이 해당 팀인 경기 추출
        mask = sched["home_team"].str.lower().str.contains(team_lower, na=False) | \
               sched["away_team"].str.lower().str.contains(team_lower, na=False)
        tm = sched.loc[mask].copy()

        # 점수 파싱 (예: 1–2 → home=1, away=2)
        tm["score"] = tm["score"].str.replace("–", "-", regex=False)
        tm = tm[tm["score"].str.contains(r"\d+\s*-\s*\d+", na=False)].copy()

        # 골 추출
        goals = tm["score"].str.extract(r"(\d+)\s*-\s*(\d+)")
        tm["home_goals"] = pd.to_numeric(goals[0], errors="coerce")
        tm["away_goals"] = pd.to_numeric(goals[1], errors="coerce")

        # 가장 최근 n경기 추출
        last_n = tm.sort_values("date").tail(n)
        if last_n.empty:
            return pd.DataFrame()

        # 골득실 요약
        records = []
        for _, row in last_n.iterrows():
            if team_lower in row["home_team"].lower():
                gf, ga = row["home_goals"], row["away_goals"]
                opp = row["away_team"]
            else:
                gf, ga = row["away_goals"], row["home_goals"]
                opp = row["home_team"]

            records.append({
                "date": row["date"].date(),
                "opponent": opp,
                "goals_for": int(gf),
                "goals_against": int(ga),
                "goal_diff": int(gf - ga)
            })

        return pd.DataFrame(records)

    def collect_features(self, match_date, home_team, away_team):
        """
        하나의 경기(Home vs Away)에 대한 주요 파생 변수 수집
        """
        match_date = pd.to_datetime(match_date)

        # 최근 경기 통계 가져오는 함수
        def get_stats(team, n):
            df = self.get_last_n_matches_goal_diff(team, 20, match_date)
            df = df.sort_values("date").tail(n)
            gf = df["goals_for"].sum()
            ga = df["goals_against"].sum()
            # 폼 점수 (승: 3, 무: 1, 패: 0)
            form = df["goal_diff"].apply(lambda x: 3 if x > 0 else 1 if x == 0 else 0).sum()
            return int(gf), int(ga), int(form)

        # 홈/원정팀 각각 3경기, 5경기 득실점 + 폼 계산
        gf3h, ga3h, form3h = get_stats(home_team, 3)
        gf5h, ga5h, form5h = get_stats(home_team, 5)
        gf3a, ga3a, form3a = get_stats(away_team, 3)
        gf5a, ga5a, form5a = get_stats(away_team, 5)

        # Elo 점수 및 변화량
        elo_home = self.get_team_elo(home_team, match_date)
        elo_away = self.get_team_elo(away_team, match_date)
        elo_diff = elo_home - elo_away if elo_home is not None and elo_away is not None else None
        elo_change_home = self.get_team_elo_change(home_team, match_date)
        elo_change_away = self.get_team_elo_change(away_team, match_date)

        # 결과 딕셔너리 구성 → DataFrame 변환
        data = {
            "MatchDate": match_date.date(),
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            "GF3Home": gf3h, "GA3Home": ga3h, "GF5Home": gf5h, "GA5Home": ga5h,
            "GF3Away": gf3a, "GA3Away": ga3a, "GF5Away": gf5a, "GA5Away": ga5a,
            "Form3Home": form3h, "Form5Home": form5h, "Form3Away": form3a, "Form5Away": form5a,
            "HomeElo": elo_home, "AwayElo": elo_away, "elo_diff": elo_diff,
            "elo_change_home": elo_change_home, "elo_change_away": elo_change_away
        }

        return pd.DataFrame([data])
