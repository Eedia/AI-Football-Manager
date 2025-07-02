import pandas as pd

# 파일 경로 설정
file_2021 = "epl_2021.csv"
file_2022 = "epl_2022.csv"
file_2023_24 = "epl_202324.csv"
file_2024_25 = "epl_202425.csv"

# CSV 파일 읽기
df_2021 = pd.read_csv(file_2021)
df_2022 = pd.read_csv(file_2022)
df_2023_24 = pd.read_csv(file_2023_24)
df_2024_25 = pd.read_csv(file_2024_25)

# 불필요한 열 제거 (2021 시즌만 해당)
if "Unnamed: 0" in df_2021.columns:
    df_2021 = df_2021.drop(columns=["Unnamed: 0"])

# 데이터프레임 병합
df_all = pd.concat([df_2021, df_2022, df_2023_24, df_2024_25], ignore_index=True)

# 통합된 데이터 저장
df_all.to_csv("epl2011-25.csv", index=False)

print("파일이 성공적으로 생성되었습니다!")
