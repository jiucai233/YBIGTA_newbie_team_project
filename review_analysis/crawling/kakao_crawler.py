# @chu20-afk
from .base_crawler import BaseCrawler
from utils.logger import logger
# in: website 주소
# out: 크롤링한 데이터, root밑에 있는 database 폴더에 csv형태로 저장, 포함해야할 항목은 
# 1별점, 
# 2날짜, 
# 3리뷰 내용
# 으로 생성해주세요!