import pandas as pd
import numpy as np

# 데이터 로드
try:
    df = pd.read_csv('EPL_2019_2025.csv')
except FileNotFoundError:
    print("Error: 'EPL_2019_2025.csv' 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
    exit()

# MatchDate를 datetime 객체로 변환하고 2021년 이후 데이터만 필터링
df['MatchDate'] = pd.to_datetime(df['MatchDate'])
df = df[df['MatchDate'].dt.year >= 2021].copy() # SettingWithCopyWarning 방지를 위해 .copy() 추가

# xG 관련 피처 목록
xg_features = [
    'h_xg', 'a_xg', 'xG_diff', 'xg_margin', 'xg_ratio',
    'rolling_xg_home_5', 'rolling_xg_away_5'
]

print("--- xG 관련 피처 결측치 현황 (2021년 이후 데이터) ---")
for col in xg_features:
    missing_count = df[col].isnull().sum()
    total_count = len(df[col])
    missing_percentage = (missing_count / total_count) * 100 if total_count > 0 else 0
    print(f"'{col}': {missing_count}개 결측 ({missing_percentage:.2f}%)")

print("\n--- 전체 데이터프레임의 결측치 요약 ---")
print(df[xg_features].isnull().sum())