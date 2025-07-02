import pandas as pd

def label_match_results(csv_path="epl_2024_xg_with_diff.csv"):
    # 전체 xG 데이터 불러오기
    df = pd.read_csv(csv_path)

    # 홈팀 기준 데이터만 추출
    df_home = df[df["venue"] == "home"].copy()

    # 라벨링: 홈팀이 기준
    def get_result(row):
        if row['xG_for'] > row['xG_against']:
            return 2  # 홈팀 승
        elif row['xG_for'] < row['xG_against']:
            return 0  # 홈팀 패
        else:
            return 1  # 무승부

    df_home["result"] = df_home.apply(get_result, axis=1)

    # 저장 및 확인
    df_home.to_csv("epl_2024_xg_labeled.csv", index=False)
    print(df_home[['date', 'team', 'opponent', 'xG_for', 'xG_against', 'xG_diff', 'result']].head())

    return df_home

if __name__ == "__main__":
    label_match_results()
