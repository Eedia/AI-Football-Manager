## 사용 라이브러리
- 'pandas' : '2.3.0'
- 'numpy' : '2.0.2'
- 'matplotlib' : '3.9.4'
- 'scikit-learn' : '1.6.1'

<Br>

## 사용 학습 모델
- ExtraTreesClassifier : feature 수는 많고 데이터 수는 적을 때 과적합 방지에 용이한 모델


<Br>

## 사용 feature
- l3 - 최근 3경기 간
- l5 - 최근 3경기 간
- diff - 해당 feature의 홈팀과 원정팀의 값차이

| 구분             | 포함된 Feature                                                                                                                                                                  | 핵심 목적                       |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| **메타 정보**      | `MatchDate`, `HomeTeam`, `AwayTeam`                                                                                                                                          | 학습 · 테스트 스플릿 / 팀 고유 효과 인코딩  |
| **전력 지표**      | `HomeElo`, `AwayElo`, `elo_diff`, `MaxHome`                                                                                                                                  | 팀 기본 실력(Elo)·시장 기대치(배당)·실력차 |
| **폼(최근 성적)**   | `Form3Home`, `Form5Home`, `Form3Away`, `Form5Away`                                                                                                                           | 최근 승점 수로 팀의 추세 파악              |
| **득 · 실점 추세**  | `GF3Home`, `GA3Home`, `GF5Home`, `GA5Home`,<br>`GF3Away`, `GA3Away`, `GF5Away`, `GA5Away`                                                                                    | 최근 경기에서 홈팀과 원정팀이 넣은 score 수            |
| **xG 지표**      | `home_xg_l3`, `home_xg_l5`, `away_xg_l3`, `away_xg_l5`,<br>`xg_l3_diff`, `xg_l5_diff`                                                                                        | 기대 득점 수준 & 양팀 비교            |
| **압박(수비 스타일)** | `home_ppda_l3`, `home_ppda_l5`, `away_ppda_l3`, `away_ppda_l5`,<br>`ppda_l3_diff`, `ppda_l5_diff`                                                                            | PPDA(Pass Allowed Per Defensive Action) : 공격 팀이 시행한 총 패스 횟수, PPDA로 압박 강도 확인              |
| **위협 지역 침투**   | `home_deep_completions_l3`, `home_deep_completions_l5`,<br>`away_deep_completions_l3`, `away_deep_completions_l5`,<br>`deep_completions_l3_diff`, `deep_completions_l5_diff` | deep completion : 크로그가 아닌 패스로, 박스권 안으로 연결되는 패스 횟수              |
| **타깃 변수**      | `FTResult`                                                                                                                                                                   | 레이블(H:0, A:1),  H-홈팀 승리, A-원정팀 승리               |


