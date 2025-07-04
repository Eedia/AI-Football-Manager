# ExtraTeesClassifier를 이용한 epl 승부 예측 모델 


<br>

## 데이터 셋
- Matches.csv
    - 2005년 부터 2025년도까지의 축구 5대 리그에 대한 데이터
    - 출처 : <a href="https://www.kaggle.com/datasets/adamgbor/club-football-match-data-2000-2025">kaggle</a>
- soccerdata 라이브러리
    - UnderStat 사이트에서 정보를 얻어온다.    
    <a href="https://understat.com/league/EPL/2023">사이트 링크</a>

<br>

## 라이브러리
- 'pandas' : '2.3.0'
- 'numpy' : '2.0.2'
- 'matplotlib' : '3.9.4'
- 'scikit-learn' : '1.6.1'
- 'soccerdata' : '1.8.7'

<br>

## 데이터 전처리

- xg_data.ipynb
    - soccerdata 라이브러리를 통해서 xG, PPDA, Deep Completions 데이터를 가져온다.
    - 가져온 xG, PPDA, Deep Completions 데이터를 최근 3경기, 5경기까지 계산한다. 
    - csv파일로 저장한다. -> xg_data.csv

<br>

- xg_data.csv 
    - xG, PPDA, Deep Completions에 관한 데이터가 담겨있는 csv파일

<br>

- data_final.csv 
    - Matchees.csv에서 필요한 column과 xg_data.csv를 합친 데이터
    - encoding만 완료될 시 바로 학습할 수 있는 전체 데이터셋이다.
    
<br>

- encoding 필요한 columns : ['HomeTeam', 'AwayTeam'] 
    - 특정 팀이 Home일 때 Away일 때를 비교하기 위해 OneHotEncoding을 진행한다.

<br>


## feature
- `_l3` **- 최근 3경기 간 평균**
- `_l5` **- 최근 5경기 간 평균**
- `_diff` **- 해당 feature의 홈팀과 원정팀의 값차이**

<br>

| 구분             | 포함된 Feature                                                                                                                                                                  | 핵심 목적                       |
| -------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------- |
| **메타 정보**      | `MatchDate`, `HomeTeam`, `AwayTeam`                                                                                                                                          | 학습 · 테스트 스플릿 / 팀 고유 효과 인코딩  |
| **전력 지표**      | `HomeElo`, `AwayElo`, `elo_diff`                                                                                                                                  | 팀 기본 실력 지표(Elo) |
| **폼(최근 성적)**   | `Form3Home`, `Form5Home`, `Form3Away`, `Form5Away`                                                                                                                           | 최근 승점 수로 팀의 추세 파악              |
| **득 · 실점 추세**  | `GF3Home`, `GA3Home`, `GF5Home`, `GA5Home`,<br>`GF3Away`, `GA3Away`, `GF5Away`, `GA5Away`                                                                                    | 최근 경기에서 홈팀과 원정팀이 넣은 골 수, 실점 수            |
| **xG 지표**      | `home_xg_l3`, `home_xg_l5`, `away_xg_l3`, `away_xg_l5`,<br>`xg_l3_diff`, `xg_l5_diff`                                                                                        | xG(Expected Goals), 기대 득점 수준 & 양팀 비교            |
| **압박(수비 스타일)** | `home_ppda_l3`, `home_ppda_l5`, `away_ppda_l3`, `away_ppda_l5`,<br>`ppda_l3_diff`, `ppda_l5_diff`                                                                            | PPDA(Pass Allowed Per Defensive Action) : <br> 상대 팀의 패스 횟수 / 우리 팀의 수비 동작(태클, 가로채기, 파울, 챌린지), PPDA가 낮을수록 압박강도가 높다.             |
| **위협 지역 침투**   | `home_deep_completions_l3`, `home_deep_completions_l5`,<br>`away_deep_completions_l3`, `away_deep_completions_l5`,<br>`deep_completions_l3_diff`, `deep_completions_l5_diff` | deep completion : 크로스가 아닌 패스로, 박스권 안으로 연결되는 패스 횟수              |
| **타깃 변수**      | `FTResult`                                                                                                                                                                   | 타겟 레이블(H, A),  H-홈팀 승리, A-원정팀 승리               |


<br><br>

## 1차 학습
preprocessing_learning_동은.ipynb 참고

데이터가 3000개 정도로 적어서 조금의 과적합을 유도하고 ensemble 중 stacking 기법을 이용해 많은 학습을 시켰다.  
<br>
<image src='./image/first learning.png'>

과적합을 조금만 유도하기 위해 가벼운 학습을 하는 lightgbm과 max_iter를 낮춘 logistic을 사용했고,
마지막에도 3개의 모델이 학습한 결과를 종합해 logistic으로 재학습했다.

<br>

<image src='./image/first learning result.png'>

정확도는 58% 정도였고, 학습 모델들이 이진분류나 다중클래스 분류에도 맞지 않았다.
또한 무승부의 확률은 승리 확률과 패배 확률이 비등한 경우에 높아져야하는데 승리, 무승부, 패배를 동시에 예측을 하면 아무리 승리 확률과 패배 확률이 비슷해져도 무승부 확률이 이 두 확률을 넘어설 수는 없었다.
그래서 무승부는 아예 예측 범위에 빼고 승리와 패배만을 예측하는 것이 정확도가 훨씬 높아졌다.

<br>

## 2차 학습 

### ExtraTreesClassifier :
  feature 수는 많고 데이터 수는 적을 때 과적합 방지에 용이한 ensemble 모델,  
  `model_final.pkl` : 학습 완료된 모델 파일
    
- 채택 이유
    - 1차 학습을 통해서 이진 분류에 적합한 모델과 적은 데이터셋으로도 학습이 가능한 모델이 필요함을 깨달았다.
    - 이진 분류에서 높은 정확도를 보이는 Random Forest Classifier는 BootStrap Sampling이라는 복원 추출 기법을 사용하기에 데이터 수가 적은 상황에서 과적합을 초래할 위험이 있다.          
    반면 BootStrap Sampling을 사용하지 않고 Random Forest Classifier에서 학습도 더 업그레이드 된 버전인 Extra Trees Classifier를 사용했다.
    - 또한 Extra Trees Classifier는 Random Forest Classifier에 비해서 특성의 중요도를 더 높게 평가한다. 그래서 핵심 fature를 가려내지 모르는 상황에서 대량의 feature를 넣고 학습시켜도 핵심 feature를 잘 발견하여 학습한다.  

<br>

- 학습 방식 :
    - Tree 방식이기 때문에 표준화, 정규와 같은 데이터 전처리는 의미가 거의 없다. 따라서 HomeTeam, AwayTeam만 OneHot Encoding을 진행하고,  ExtraTreesClassifier를 통해 학습했다.

    - ExtraTreesClassifier는 여러 개의 독립된 랜덤 트리를 만들고 모든 트리의 결과를 평균을 내는 방식을 사용한다.  
각 트리를 충분히 학습시키고 마지막에 랜덤한 결과를 산출하면 이 결과를 모아 평균을 낸다.   
ExtraTreesClassifier는 충분히 학습한 트리가 랜덤한 결과를 내놓은 것 같아도 근거가 있어서 해당 결과가 나왔을 것이라는 가설을 통해 이를 모아 평균을 낸다. 이는 실제로도 좋은 결과를 만들어낸다.   

    - 마치 한 분야에 대한 수백명의 전문가를 모아놓고, 이들에게 같은 문제를 고민하게 만들면 평균적으로 같은(좋은) 결과에 수렴하는 것과 같은 원리이다.


### 파라미터 
- 파라미터는 ReandomizedSearchCV를 통해서 대략적으로 정하고 이후에 반복 미세 조정으로 현재의 파라미터 값을 얻었다.

<br>

| 파라미터   | 값                                                                                   |
| ------ | ------ | 
| n_estimators  | 1900  |
|  max_depth  |  10 |
| max_features   |  0.25 |
| min_samples_leaf   | 15  |
| n_jobs   |  -1 |
|  class_weight  |  balanced_subsample |
|  random_state  |  42 |

<br>




   