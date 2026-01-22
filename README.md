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
서울 잠실동에 있는 놀이공원인 '롯데월드'의 리뷰를 세 사이트에서 크롤링 및 분석하고자 하였습니다.  
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
### 텍스트 벡터화

# 시각화 도표 및 설명
## EDA
### Kakao
![Getting Started](review_analysis/plots/preprocessed_reviews_kakao_rating_distribution.png)
  - 5점 평점이 250건 이상으로 압도적으로 많으며, 2점이 가장 적은 빈도를 보입니다. 데이터가 고득점에 집중된 **긍정적 편향(Positive Bias)**을 띠고 있어, 전반적인 서비스 만족도가 높음을 시사합니다.
### Google
![Getting Started](review_analysis/plots/preprocessed_reviews_google_rating_distribution.png)
  - 5점 평점이 250건 이상으로 압도적으로 많으며, 2점이 가장 적은 빈도를 보입니다. 데이터가 고득점에 집중된 **긍정적 편향(Positive Bias)**을 띠고 있어, 전반적인 서비스 만족도가 높음을 시사합니다.
### Tripdotcom
![Getting Started](review_analysis/plots/preprocessed_reviews_tripdotcomrating_distribution.png)
  - 5점 만점이 압도적으로 많으며, 고득점에 치중된 **긍정적 편향(Positive Bias)**을 보이고 있습니다. 이는 전반적인 서비스 만족도가 매우 높음을 시사합니다.

## 전처리/FE
### Kakao
![Getting started]()
![Getting started]()

### Google
![Getting started](review_analysis/plots/preprocessed_reviews_google_rating_distribution.png)
![Getting started](review_analysis/plots/preprocessed_reviews_google_review_length_distribution.png)



### Tripdotcom
![Getting started](review_analysis/plots/preprocessed_reviews_tripdotcomreview_length_distribution.png)
대부분의 리뷰가 0~50자 사이의 짧은 길이로 작성되었음을 알 수 있다. 사용자들이 주로 간결한 후기를 남기는 경향이 높음을 시사한다.
![Getting started](review_analysis/plots/preprocessed_reviews_tripdotcomreviews_by_month.png)
월별 작성된 리뷰의 개수를 보았을 때, 8월에 리뷰 수가 가장 높으며 10월과 12월에도 비교적 높은 수치를 기록한다. 이를 통해 여름 휴가철이나 연말 시즌에 방문이 활발해지는 패턴을 보여준다.
![Getting started](review_analysis/plots/preprocessed_reviews_tripdotcomreviews_by_weekday.png)
요일별 리뷰 등록 빈도를 비교했을 때, 비교적 월요일과 화요일에 리뷰가 가장 많이 등록된 것을 확인할 수 있다. 주말에 방문한 관람객들이 방문 직후인 주 초반에 후기를 남기는 사용자가 많음을 유추할 수 있다.
![Getting started](review_analysis/plots/reviews_tripdotcom_tfidf_embeddings_top_doc_freq.png)
전체 리뷰 중 해당 단어가 포함된 리뷰의 비율이 높은 상위 20개 단어를 추출한 그래프이다. '정말', '좋은', '너무', '즐거운'과 같이 감정을 나타내는 부사나 형용사가 상위권을 차지하고 있다. 또한, 롯데월드와 관련된 '실내', '놀이기구' 등의 키워드를 통해 데이터의 정체성을 파악할 수 있다.

## 비교분석
*구글 데이터의 날짜가 "몇년 전"으로 보임을따라, 데이터를 처리하는 날짜를 기준으로 x년 전으로 이동하여 날짜 변수를 생성하였습니다
### 텍스트 분석
![Getting started](review_analysis/plots/comparison_content_length_distribution.png)
![Getting started](review_analysis/plots/comparison_rating_distribution.png)
### 시계열 분석
![Getting started](review_analysis/plots/comparison_reviews_by_month.png)
![Getting started](review_analysis/plots/comparison_reviews_by_weekday.png)
