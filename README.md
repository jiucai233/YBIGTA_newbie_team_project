## YBIGTA 4th team
Team lead: 신영군
Team member: 배순은 양진완

### Team Information
we good

### Member Introduction
신영군: YBIGTA 28기 신영군입니다! 반갑습니다  
양진완: YBIGTA 28기 양진완입니다! 화이팅해봐요  
배순은: YBIGTA 28기 배순은입니다! 파이팅입니다ㅠㅠ!  

## Image attatched
branch protection(branch rule)
![Getting Started](github/branch_protection.png)
rejected push request
![Getting Started](github/push_rejected.png)
review and merge
![Getting Started](github/review_and_merged.png)

## 코드 실행 방법

1. 터미널 또는 Powershell 열기
2. 경로 설정 (YBIGTA_newbie_team_project 루트폴더)
3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 크롤링
```bash
python -m review_analysis.crawling.main -o database --all
```
### EDA/FE
```bash
python -m review_analysis.preprocessing.main --output_dir database --all
```

## 데이터 소개 
서울 잠실동에 있는 놀이공원인 '롯데월드'의 리뷰를 세 사이트에서 크롤링 및 분석하고자 하였습니다.
### 크롤링한 사이트 링크
   - 구글맵: https://www.google.com/maps/place/Lotte+World/data=!4m12!1m2!2m1!1sLotte+World!3m8!1s0x357ca5a7250efe81:0x433df2c1fec03b98!8m2!3d37.5111158!4d127.098167!9m1!1b1!15sCgtMb3R0ZSBXb3JsZCIDiAEBWg0iC2xvdHRlIHdvcmxkkgEKdGhlbWVfcGFya-ABAA!16zL20vMDNqbGo5?hl=en&entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D  
   - 카카오맵: https://place.map.kakao.com/27560699
   - 트립닷컴: https://kr.trip.com/travel-guide/attraction/seoul/lotte-world-adventure-136469953/
### 데이터 형식
    - 사이트별 크롤링 결과를 각각의 csv 파일로 저장
### 데이터 개수
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

## WEB homework usage guide

## Crawling homework usage guide

## EDA/FE homework usage guide

## Appendix (additional info)

### 트립닷컴 리뷰 데이터 소개

- 크롤링 사이트 링크: https://kr.trip.com/travel-guide/attraction/seoul/lotte-world-adventure-136469953/
- 컬럼: rating, date, content
- 데이터 형식: rating - int, date - string/date, content - string
- 데이터 개수: 500개(사이트 제한으로 500개까지만 수집 가능)

### 실행 방법

1. 프로그램이 실행되면 브라우저가 자동으로 실행됩니다. 
2. 브라우저가 로딩된 이후 자동으로 리뷰 부분까지 스크롤을 진행합니다.
3. 리뷰 섹션을 발견했다면 크롤링을 시작합니다.

### 카카오맵 리뷰 데이터 소개 (Crawling)

- 크롤링 사이트 링크: https://place.map.kakao.com/27560699
- 데이터 형식: CSV
- 데이터 개수: 500개 이상
- 컬럼: rating, date, content
- 저장 위치: database/reviews_kakao.csv

### 실행 방법

```bash
python -m review_analysis.crawling.main -o . -c kakao
```


