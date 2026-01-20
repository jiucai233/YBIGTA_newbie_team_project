## YBIGTA 4th team
Team lead: 신영군
Team member: 배순은 양진완

### Team Information
we good

### Member Introduction
신영군: YBIGTA 28기 신영군입니다! 반갑습니다  
양진완: YBIGTA 28기 양진완입니다! 화이팅해봐요  
배순은: YBIGTA 28기 배순은입니다! 파이팅입니다ㅠㅠ!

## 카카오맵 리뷰 데이터 소개 (Crawling)

- 크롤링 사이트 링크: https://place.map.kakao.com/27560699
- 데이터 형식: CSV
- 데이터 개수: 500개 이상
- 컬럼: rating, date, content
- 저장 위치: database/reviews_kakao.csv

## 실행 방법

```bash
python -m review_analysis.crawling.main -o . -c kakao
```

## 트립닷컴 리뷰 데이터 소개

- 크롤링 사이트 링크: https://kr.trip.com/travel-guide/attraction/seoul/lotte-world-adventure-136469953/
- 컬럼: rating, date, content
- 데이터 형식: rating - int, date - string/date, content - string
- 데이터 개수: 500개(사이트 제한으로 500개까지만 수집 가능)

## 실행 방법

1. 프로그램이 실행되면 브라우저가 자동으로 실행됩니다. 
2. 브라우저가 자동으로 리뷰까지 스크롤을 시도하고, 리뷰를 찾았다면 크롤링을 시작합니다.