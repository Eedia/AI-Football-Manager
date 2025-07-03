import pandas as pd

df = pd.read_csv("EPL_2019_2025.csv")
team_list = sorted(set(df["HomeTeam"].unique()) | set(df["AwayTeam"].unique()))

print(team_list)