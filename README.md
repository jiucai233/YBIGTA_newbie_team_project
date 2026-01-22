# YBIGTA 4th team
Team lead: 신영군
Team member: 배순은 양진완

# Team Information
we good

# Member Introduction
신영군: YBIGTA 28기 신영군입니다! 반갑습니다  
양진완: YBIGTA 28기 양진완입니다! 화이팅해봐요  
배순은: YBIGTA 28기 배순은입니다! 파이팅입니다ㅠㅠ!  

# Github homework image
branch protection(branch rule)
![Getting Started](github/branch_protection.png)
rejected push request
![Getting Started](github/push_rejected.png)
review and merge
![Getting Started](github/review_and_merged.png)

# 코드 실행 방법

## 환경 준비

1. 터미널 또는 Powershell 열기
2. 경로 설정 (YBIGTA_newbie_team_project 루트폴더)
3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```
## WEB 과제

## 크롤링
```bash
cd review_analysis/crawling
python main.py --output_dir ../../database --all
```

## EDA/FE
```bash
cd review_analysis/preprocessing  
python main.py --output_dir ../../database --all
```

# 데이터 소개 
서울 잠실동에 있는 놀이공원인 '롯데월드'의 리뷰를 세 사이트에서 크롤링 및 분석하고자 하였다. 
#### 크롤링한 사이트 링크
   - 구글맵: https://www.google.com/maps/place/Lotte+World/data=!4m12!1m2!2m1!1sLotte+World!3m8!1s0x357ca5a7250efe81:0x433df2c1fec03b98!8m2!3d37.5111158!4d127.098167!9m1!1b1!15sCgtMb3R0ZSBXb3JsZCIDiAEBWg0iC2xvdHRlIHdvcmxkkgEKdGhlbWVfcGFya-ABAA!16zL20vMDNqbGo5?hl=en&entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D  
   - 카카오맵: https://place.map.kakao.com/27560699
   - 트립닷컴: https://kr.trip.com/travel-guide/attraction/seoul/lotte-world-adventure-136469953/
#### 데이터 형식
    - 사이트별 크롤링 결과를 각각의 csv 파일로 저장
#### 데이터 개수
    - 구글맵: 776개
    - 카카오맵: 661개
    - 트립닷컴: 500개

## 전처리/FE
### 결측치
   - `rating`, `review`, `date` 컬럼에서 결측치가 있는 행 제거
### 이상치
   - 별점이 1부터 5까지의 정수가 아닌 경우 데이터 제거  
### 텍스트데이터 전처리
   - 이모티콘 등과 같은 특수문자 제거 및 불필요한 공백 삭제  
### 파생변수
   - 리뷰 길이
   - 긍정/부정 여부(별점이 4점 이상일 경우 긍정으로 분류)
   - 시계열분석을 위한 '월' 및 '요일' 변수
### 텍스트 벡터화 (TF-IDF)
   리뷰 텍스트를 TF-IDF 방식으로 벡터화하여 각 리뷰를 단어 가중치 벡터로 표현했다. 이렇게 만든 TF-IDF 임베딩(embedding) CSV를 기반으로 
   (1) 평균 TF-IDF가 큰 상위 단어, 
   (2) 문서 등장 비율이 큰 상위 단어를 시각화하고, 
   (3) 벡터의 희소도(sparsity) 및 리뷰당 유효 단어 수 같은 기본 통계를 확인했다. 
   또한 PCA 2차원 산점도로 임베딩 분포를 살펴보았고, 사이트가 2개 이상일 경우 사이트 간 단어집합 교집합/합집합 및 Jaccard 유사도, 공통 단어의 평균 TF-IDF 차이가 큰 단어들을 비교 분석했다. 
   결과(그래프 PNG)는 review_analysis/plots/에 저장했음.

# 시각화 도표 및 설명
## EDA
### Kakao
![Getting Started](review_analysis/plots/preprocessed_reviews_kakao_rating_distribution.png)
5점 평점이 250건 이상으로 압도적으로 많으며, 2점이 가장 적은 빈도를 보인다. 데이터가 고득점에 집중된 **긍정적 편향(Positive Bias)**을 띠고 있어, 전반적인 서비스 만족도가 높음을 시사한다.
### Google
![Getting Started](review_analysis/plots/preprocessed_reviews_google_rating_distribution.png)
5점 평점이 250건 이상으로 압도적으로 많으며, 2점이 가장 적은 빈도를 보인다. 데이터가 고득점에 집중된 **긍정적 편향(Positive Bias)**을 띠고 있어, 전반적인 서비스 만족도가 높음을 시사한다.
### Tripdotcom
![Getting Started](review_analysis/plots/preprocessed_reviews_tripdotcomrating_distribution.png)
두 데이터 모두 5점 만점이 압도적으로 많으며, 고득점에 치중된 **긍정적 편향(Positive Bias)**을 보이고 있다. 이는 전반적인 서비스 만족도가 매우 높음을 시사하며, 데이터 정리를 통해 시각화가 가능해진 상태를 잘 보여준다.

## 전처리/FE
### Kakao
![Getting started](review_analysis/plots/preprocessed_reviews_kakao_rating_distribution.png)
5점 리뷰의 비중이 가장 높아 전반적으로 이용자의 만족도가 높고, 1점과 5점에 리뷰가 집중되는 양극화된 분포가 관찰되었다.
![Getting started](review_analysis/plots/reviews_kakao_tfidf_embeddings_pca_2d.png)
PCA 결과, 설명된 분산은 2% 뿐이고 이는 텍스트 정보가 고차원에 분산되어 있음을 의미한다.
점들이 왼쪽에 몰려있고, 일부만 멀리 튀어나왔다. 대부분의 리뷰가 비슷한 단어 조합이고, 소수의 리뷰만 다른 단어를 사용함을 의미한다.
![Getting started](review_analysis/plots/reviews_kakao_tfidf_embeddings_top_doc_freq.png)
Doc frequency 상위 단어들은 ‘너무’, ‘좋아요’, ‘사람’ 등 많은 리뷰에서 반복되는 일반적인 감정 및 구어 표현이다. 플랫폼 특성을 반영한 공통 키워드로 볼 수 있다.
플랫폼 특성을 반영한 공통 키워드이다.
![Getting started](review_analysis/plots/reviews_kakao_tfidf_embeddings_top_mean_tfidf.png)
Mean TF-IDF 기준 상위 단어들은 ‘롯데월드’, ‘매직패스’, ‘놀이기구’ 등 리뷰의 핵심 경험과 직접적으로 연결된 단어들로, 카카오 리뷰의 주된 내용이 놀이공원 체험임을 보여준다.

### Google
![Getting started](review_analysis/plots/preprocessed_reviews_google_rating_distribution.png)
![Getting started](review_analysis/plots/preprocessed_reviews_google_review_length_distribution.png)



### Tripdotcom
![Getting started](review_analysis/plots/preprocessed_reviews_tripdotcomreview_length_distribution.png)
![Getting started](review_analysis/plots/preprocessed_reviews_tripdotcomreviews_by_month.png)
![Getting started](review_analysis/plots/preprocessed_reviews_tripdotcomreviews_by_weekday.png)
![Getting started](review_analysis/plots/reviews_tripdotcom_tfidf_embeddings_top_doc_freq.png)
![Getting started]()
![Getting started]()

## 비교분석
*구글 데이터의 날짜가 "몇년 전"으로 보임을따라, 데이터를 처리하는 날짜를 기준으로 x년 전으로 이동하여 날짜 변수를 생성하였습니다
### 텍스트 분석
![Getting started](review_analysis/plots/comparison_content_length_distribution.png)
![Getting started](review_analysis/plots/comparison_rating_distribution.png)
### 시계열 분석
![Getting started](review_analysis/plots/comparison_reviews_by_month.png)
![Getting started](review_analysis/plots/comparison_reviews_by_weekday.png)
