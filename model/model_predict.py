import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# 1. 데이터 로딩 및 전처리
df = pd.read_csv('EPL_2019_2025.csv')
df['MatchDate'] = pd.to_datetime(df['MatchDate'])
df = df[df['MatchDate'].dt.year >= 2021]  # 최근 3시즌만 사용

# 수정된 피처 목록
features = [
    'HomeElo', 'AwayElo', 'elo_diff',
    'Form3Home', 'Form5Home', 'Form3Away', 'Form5Away',
    'h_xg', 'a_xg', 'xG_diff', 'xg_margin', 'xg_ratio',
    'rolling_xg_home_5', 'rolling_xg_away_5',
    'elo_change_home', 'elo_change_away'
]

# 결측치 제거
df = df.dropna(subset=features + ['result'])

X = df[features]
y = (df['result'] == 2).astype(int)  # 홈팀 승리 여부 (2 = 홈승)

print(len(X), "rows of data loaded.")
# 2. 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 3. 모델 학습
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    use_label_encoder=False,
    eval_metric='logloss'
)
model.fit(X_train, y_train)

# 4. 예측 및 평가
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("Accuracy:", acc)
print("\nClassification Report:\n", report)
print("\nConfusion Matrix:\n", cm)

# 5. 모델 저장
joblib.dump(model, 'xgb_model.pkl')