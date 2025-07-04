import pandas as pd
from soccerdata import ClubElo
from concurrent.futures import ThreadPoolExecutor

class DataCollector:
    def __init__(self):
        # Elo 객체 및 캐시 준비
        self.clubelo = ClubElo()
        self.elo_cache = {}

    def get_team_elo(self, team_name, match_date):
        # 경기 전날 Elo 조회
        d = pd.to_datetime(match_date) - pd.Timedelta(days=1)
        if d not in self.elo_cache:
            df = self.clubelo.read_by_date(date=d).reset_index()
            self.elo_cache[d] = df
        df = self.elo_cache[d]
        match = df[df['team'].str.lower() == team_name.lower()]
        return match.iloc[0]['elo'] if not match.empty else None

    def collect_features(self, match_date, home_team, away_team):
        # 날짜 기준 변환
        dt = pd.to_datetime(match_date)

        # 홈/어웨이 스탯 및 Elo 병렬 조회
        with ThreadPoolExecutor() as exe:
            f_elo_h = exe.submit(self.get_team_elo, home_team, dt)
            f_elo_a = exe.submit(self.get_team_elo, away_team, dt)

            elo_h = f_elo_h.result()
            elo_a = f_elo_a.result()

        # 결과 딕셔너리 구성
        result = {
            'MatchDate': dt.date(),
            'HomeTeam': home_team,
            'AwayTeam': away_team,

            'HomeElo': elo_h,
            'AwayElo': elo_a,
            'elo_diff': (elo_h - elo_a) if elo_h is not None and elo_a is not None else None
        }

        return pd.DataFrame([result])
