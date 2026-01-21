import time
import random
import re
import sys
import pandas as pd
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_crawler import BaseCrawler
from utils.logger import setup_logger

logger = setup_logger('trip_dot_com')

class TripDotComCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.logger = logger
        self.driver: Optional[webdriver.Chrome] = None
        self.data: List[Dict[str, Any]] = []
        
        # 윈도우 인코딩 설정 유지
        if sys.platform == "win32":
            try:
                sys.stdout.reconfigure(encoding='utf-8') # type: ignore
            except AttributeError:
                import io
                sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', line_buffering=True) # type: ignore

    def start_browser(self):
        """
        브라우저를 실행합니다
        """
        logger.info("브라우저를 실행합니다.")
        options = Options()
        # GoogleCrawler에서 사용한 표준 안정화 옵션 적용
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        try:
            self.driver = webdriver.Chrome(options=options)
            
            # 브라우저 감지 회피 자바스크립트
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 대기 시간 설정
            self.driver.implicitly_wait(10)
            self.driver.maximize_window()
            logger.info("브라우저 초기화 완료.")
            
        except Exception as e:
            logger.error(f"브라우저 실행 실패: {e}")
            raise

    def format_date(self, raw_date_str) -> str:
        """
        날짜 문자열을 'YYYY-MM-DD' 형식으로 변환합니다.
        예: '2023년 8월 15일' -> '2023-08-15'

        Args:
            raw_date_str (str): 원본 날짜 문자열

        Returns:
            str: 변환된 날짜 문자열
        """
        try:
            numbers = re.findall(r'\d+', raw_date_str)
            if len(numbers) >= 3:
                return f"{numbers[0]}-{numbers[1].zfill(2)}-{numbers[2].zfill(2)}"
            return raw_date_str
        except:
            return raw_date_str

    def scrape_reviews(self):
        """
        브라우저에서 리뷰 데이터를 자동으로 스크롤하여 수집합니다.
        """
        if self.driver is None:
            self.start_browser()

        url = "https://kr.trip.com/travel-guide/attraction/seoul/lotte-world-adventure-136469953/"
        self.driver.get(url)
        
        wait = WebDriverWait(self.driver, 20)
        
        # --- 자동 스크롤 로직 추가 ---
        self.logger.info("리뷰 섹션을 찾는 중입니다... 자동으로 스크롤합니다.")
        found_reviews = False
        max_attempts = 10  # 최대 스크롤 시도 횟수
        
        for i in range(max_attempts):
            try:
                # 리뷰 컨테이너가 있는지 확인 (이미 존재하면 스크롤 중단)
                review_elements = self.driver.find_elements(By.CLASS_NAME, "gl-poi-detail_comment-content")
                if len(review_elements) > 0:
                    self.logger.info("리뷰 섹션을 발견했습니다.")
                    found_reviews = True
                    break
                
                # 리뷰가 없으면 아래로 1000픽셀씩 스크롤
                self.driver.execute_script("window.scrollBy(0, 1000);")
                self.logger.info(f"스크롤 중... ({i+1}/{max_attempts})")
                time.sleep(1.5) # 로딩 대기
            except Exception as e:
                self.logger.warning(f"스크롤 중 알 수 없는 오류 발생: {e}")

        if not found_reviews:
            self.logger.error("리뷰 섹션을 찾지 못했습니다. 수집을 중단합니다.")
            return
        
        while len(self.data) < 600:
            try:
                # 1. 리뷰 리스트 로딩 대기
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "gl-poi-detail_comment-content")))
                time.sleep(random.uniform(2, 4))
                
                # 2. 현재 페이지 리뷰 데이터 추출
                reviews = self.driver.find_elements(By.CSS_SELECTOR, "div.gl-poi-detail_comment-content")
                
                for rev in reviews:
                    if len(self.data) >= 600: break
                    try:
                        # 별점 추출
                        rating = rev.find_element(By.CSS_SELECTOR, "span.review_score").text
                        # 날짜 추출
                        raw_date = rev.find_element(By.CLASS_NAME, "create-time").text
                        formatted_date = self.format_date(raw_date)
                        # 리뷰 내용 추출
                        content = rev.find_element(By.CSS_SELECTOR, "p.hover-pointer").text.replace('\n', ' ').strip()

                        if content:
                            self.data.append({
                                "rating": rating,
                                "date": formatted_date,
                                "content": content
                            })
                    except:
                        continue

                self.logger.info(f"현재 총 {len(self.data)}개 수집 확보")

                # 3. 다음 페이지 이동 버튼 클릭
                if len(self.data) < 600:
                    try:
                        next_btn_selector = "div.gl-poi-detail_page button.btn-next"
                        next_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, next_btn_selector)))
                        
                        # 버튼이 'disabled' 상태인지 확인 (마지막 페이지 체크)
                        if "disabled" in next_btn.get_attribute("class") or next_btn.get_attribute("disabled"):
                            self.logger.info("마지막 리뷰 페이지에 도달했습니다.")
                            break
                            
                        # 버튼이 가려지지 않게 중앙으로 스크롤 후 클릭
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
                        time.sleep(1)
                        self.driver.execute_script("arguments[0].click();", next_btn)
                        
                        # 페이지 로딩 시간 대기
                        time.sleep(random.uniform(4, 6))
                        
                    except Exception as e:
                        self.logger.warning(f"다음 페이지 버튼 클릭 실패: {e}")
                        print("\n수동으로 리뷰 목록 하단의 '>' 버튼을 클릭한 뒤 Enter를 누르세요 ('q'는 종료):")
                        if input().lower() == 'q': break
                
            except Exception as e:
                self.logger.error(f"수집 루프 오류 발생: {e}")
                break
        
        self.logger.info(f"수집 완료: 총 {len(self.data)}개")
        try:
            if self.driver: self.driver.quit()
        except: pass

    def save_to_database(self):
        """
        추출한 데이터를 CSV 파일로 저장합니다.
        """
        if not self.data: 
            self.logger.warning("저장할 데이터가 없습니다.")
            return
        df = pd.DataFrame(self.data)
        file_path = f"{self.output_dir}/reviews_tripdotcom.csv"
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        self.logger.info(f"데이터 저장 완료: {file_path}")