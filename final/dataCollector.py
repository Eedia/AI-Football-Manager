import pandas as pd
from soccerdata import ClubElo, Understat
from concurrent.futures import ThreadPoolExecutor

'''
데이터 수집하는 클래스 -> 통합버전 (elo, xG, 기타 피처)
'''
class DataCollector:
    def __init__(self):
        self.clubelo = ClubElo()
        self.elo_cache = {}

        self.us = Understat(leagues=["ENG-Premier League"], seasons=range(2024, 2026))
        self.us_data = self._load_understat_data()

    def _load_understat_data(self):
        m = self.us.read_team_match_stats()[[
            'game_id', 'date', 'home_team', 'away_team',
            'home_goals', 'away_goals',
            'home_xg', 'away_xg',
            'home_points', 'away_points'
        ]]
        m['date'] = pd.to_datetime(m['date'])

        # 롱 포맷으로 변환
        home = m.assign(
            team=m['home_team'], goals=m['home_goals'], GA=m['away_goals'],
            xg=m['home_xg'], points=m['home_points'], side='home'
        )[['game_id', 'date', 'team', 'side', 'goals', 'GA', 'xg', 'points']]

        away = m.assign(
            team=m['away_team'], goals=m['away_goals'], GA=m['home_goals'],
            xg=m['away_xg'], points=m['away_points'], side='away'
        )[['game_id', 'date', 'team', 'side', 'goals', 'GA', 'xg', 'points']]

        long_df = pd.concat([home, away], ignore_index=True)

        def add_rolling(g):
            g = g.sort_values('date', ascending=False)
            for w in (3, 5):
                g[f'GF{w}'] = g['goals'].rolling(w, min_periods=1).sum().shift(1)
                g[f'GA{w}'] = g['GA'].rolling(w, min_periods=1).sum().shift(1)
                g[f'Form{w}'] = g['points'].rolling(w, min_periods=1).sum().shift(1)
            g['rolling_xg_5'] = g['xg'].rolling(5, min_periods=1).mean()
            g['current_xg'] = g['xg']
            return g

        long_roll = long_df.groupby('team', group_keys=False).apply(add_rolling)

        home_w = long_roll[long_roll['side'] == 'home'][[
            'game_id', 'date', 'team', 'rolling_xg_5', 'Form3', 'Form5',
            'GF3', 'GF5', 'GA3', 'GA5', 'current_xg'
        ]].rename(columns={
            'team': 'HomeTeam',
            'rolling_xg_5': 'rolling_xg_home_5',
            'current_xg': 'h_xg',
            'Form3': 'Form3Home', 'Form5': 'Form5Home',
            'GF3': 'GF3Home', 'GF5': 'GF5Home',
            'GA3': 'GA3Home', 'GA5': 'GA5Home'
        })

        away_w = long_roll[long_roll['side'] == 'away'][[
            'game_id', 'date', 'team', 'rolling_xg_5', 'Form3', 'Form5',
            'GF3', 'GF5', 'GA3', 'GA5', 'current_xg'
        ]].rename(columns={
            'team': 'AwayTeam',
            'rolling_xg_5': 'rolling_xg_away_5',
            'current_xg': 'a_xg',
            'Form3': 'Form3Away', 'Form5': 'Form5Away',
            'GF3': 'GF3Away', 'GF5': 'GF5Away',
            'GA3': 'GA3Away', 'GA5': 'GA5Away'
        })

        feat_df = pd.merge(home_w, away_w, on=['game_id', 'date'], how='inner')
        feat_df = feat_df.rename(columns={'date': 'MatchDate'})
        feat_df['MatchDate'] = feat_df['MatchDate'].dt.date

        # 파생 변수
        feat_df['xG_diff'] = feat_df['h_xg'] - feat_df['a_xg']
        feat_df['xg_margin'] = feat_df['xG_diff'].abs()
        feat_df['xg_ratio'] = feat_df['h_xg'] / (feat_df['a_xg'] + 1e-6)

        return feat_df

    def get_team_elo(self, team_name, match_date):
        d = pd.to_datetime(match_date) - pd.Timedelta(days=1)
        if d not in self.elo_cache:
            df = self.clubelo.read_by_date(date=d).reset_index()
            self.elo_cache[d] = df
        df = self.elo_cache[d]
        match = df[df['team'].str.lower() == team_name.lower()]
        return match.iloc[0]['elo'] if not match.empty else None

    def collect_features(self, match_date, home_team, away_team):
        dt = pd.to_datetime(match_date)

        with ThreadPoolExecutor() as exe:
            f_elo_h = exe.submit(self.get_team_elo, home_team, dt)
            f_elo_a = exe.submit(self.get_team_elo, away_team, dt)

            elo_h = f_elo_h.result()
            elo_a = f_elo_a.result()

        result = {
            'MatchDate': dt.date(),
            'HomeTeam': home_team,
            'AwayTeam': away_team,
            'HomeElo': elo_h,
            'AwayElo': elo_a,
            'elo_diff': (elo_h - elo_a) if elo_h is not None and elo_a is not None else None
        }

        return pd.DataFrame([result])

    def data_collector(self, df):
        df = df.copy()
        team_name_map = {
            'Man United': 'Manchester United',
            'Tottenham': 'Tottenham',
            'Spurs': 'Tottenham',
            'Wolves': 'Wolverhampton Wanderers',
            'Leeds': 'Leeds United',
            'Newcastle': 'Newcastle United',
            'Nottm Forest': 'Nottingham Forest',
            'Brighton': 'Brighton',
        }

        df['HomeTeam'] = df['HomeTeam'].replace(team_name_map)
        df['AwayTeam'] = df['AwayTeam'].replace(team_name_map)

        self.us_data['HomeTeam'] = self.us_data['HomeTeam'].replace(team_name_map)
        self.us_data['AwayTeam'] = self.us_data['AwayTeam'].replace(team_name_map)

        df_merged = pd.merge(df, self.us_data, on=['MatchDate', 'HomeTeam', 'AwayTeam'], how='left')
        df_merged.fillna(0, inplace=True)
        return df_merged