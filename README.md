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
