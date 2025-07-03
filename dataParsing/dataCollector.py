import pandas as pd
import soccerdata as sd

class DataCollector: 
    def __init__(self):
        self.fbref = sd.FBref(
            leagues="ENG-Premier League",
            seasons="2425",  # 2024-2025 시즌
            no_cache=True
        )
        self.clubelo = sd.ClubElo()
        self.team_name_map = {
            "Arsenal": "Arsenal",
            "Aston Villa": "Aston Villa",
            "Bournemouth": "Bournemouth",
            "Brentford": "Brentford",
            "Brighton": "Brighton",
            "Chelsea": "Chelsea",
            "Crystal Palace": "Crystal Palace",
            "Everton": "Everton",
            "Fulham": "Fulham",
            "Leeds United": "Leeds United",
            "Liverpool": "Liverpool",
            "Man City": "Man City",
            "Man Utd": "Man Utd",
            "Newcastle": "Newcastle",
            "Nottingham Forest": "Nottingham Forest",
            "Southampton": "Southampton",
            "Spurs": "Spurs",
            "West Ham": "West Ham",
            "Wolves": "Wolves"
        }

    def get_team_elo(self, team_alias, match_date):
        official_name = self.team_name_map.get(team_alias, team_alias)
        match_date = pd.to_datetime(match_date)
        day_before = match_date - pd.Timedelta(days=1)

        try:
            df = self.clubelo.read_by_date(date=day_before).reset_index()
        except Exception as e:
            print(f"Elo 데이터 로딩 실패: {e}")
            return None

        filtered = df[df["team"].str.lower() == official_name.lower()]
        if filtered.empty:
            print(f"Elo 데이터 없음: {official_name} on {day_before.date()}")
            return None
        return filtered.iloc[0]["elo"]

    def get_last_n_matches_goal_diff(self, team_name, n):
        sched = self.fbref.read_schedule().reset_index()
        team_lower = team_name.lower()

        mask = sched["home_team"].str.lower().str.contains(team_lower, na=False) \
            | sched["away_team"].str.lower().str.contains(team_lower, na=False)
        tm = sched.loc[mask].copy()

        tm["date"] = pd.to_datetime(tm["date"])
        tm = tm.sort_values("date")
        tm["score"] = tm["score"].str.replace("–", "-", regex=False)
        tm = tm[tm["score"].str.contains(r"\d+\s*-\s*\d+", na=False)].copy()

        goals = tm["score"].str.extract(r"(\d+)\s*-\s*(\d+)")
        tm["home_goals"] = pd.to_numeric(goals[0], errors="coerce")
        tm["away_goals"] = pd.to_numeric(goals[1], errors="coerce")

        last_n = tm.tail(n)
        if last_n.empty:
            return pd.DataFrame()

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
        match_date = pd.to_datetime(match_date)

        def get_stats(team, n):
            df = self.get_last_n_matches_goal_diff(team, 20)
            df = df[df["date"] < match_date.date()]
            df = df.sort_values("date").tail(n)
            gf = df["goals_for"].sum()
            ga = df["goals_against"].sum()
            form = df["goal_diff"].apply(lambda x: 3 if x > 0 else 1 if x == 0 else 0).sum()
            return int(gf), int(ga), int(form)

        gf3h, ga3h, form3h = get_stats(home_team, 3)
        gf5h, ga5h, form5h = get_stats(home_team, 5)
        gf3a, ga3a, form3a = get_stats(away_team, 3)
        gf5a, ga5a, form5a = get_stats(away_team, 5)

        elo_home = self.get_team_elo(home_team, match_date)
        elo_away = self.get_team_elo(away_team, match_date)

        data = {
            "MatchDate": match_date.date(),
            "HomeTeam": home_team,
            "AwayTeam": away_team,
            "GF3Home": gf3h,
            "GA3Home": ga3h,
            "GF5Home": gf5h,
            "GA5Home": ga5h,
            "GF3Away": gf3a,
            "GA3Away": ga3a,
            "GF5Away": gf5a,
            "GA5Away": ga5a,
            "Form3Home": form3h,
            "Form5Home": form5h,
            "Form3Away": form3a,
            "Form5Away": form5a,
            "HomeElo": elo_home,
            "AwayElo": elo_away
        }

        return pd.DataFrame([data])