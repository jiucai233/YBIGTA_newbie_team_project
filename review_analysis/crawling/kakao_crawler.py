# @chu20-afk
from .base_crawler import BaseCrawler
from utils.logger import setup_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time, re
import os
import pandas as pd # type: ignore
from bs4 import BeautifulSoup

logger = setup_logger()


class KakaoCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        """
        Selenium ChromeDriver를 실행하여 브라우저를 여는 메서드
        self.driver에 WebDriver 객체를 저장
        """
        super().__init__(output_dir)

        # 나중에 start_browser()에서 webdriver 객체를 넣어둘 자리
        self.driver = None

        # scrape_reviews()에서 긁어온 리뷰들을 담아둘 리스트
        self.reviews: list[dict[str, str]] = []

    def start_browser(self):
        """
        카카오맵 장소 페이지에서 리뷰를 크롤링하는 메서드

        - 카카오맵이 사진 탭으로 이동하는 문제를 방지하기 위해
          후기(리뷰) 화면으로 강제 전환
        - 스크롤을 통해 동적으로 로딩되는 리뷰를 반복적으로 수집
        - 각 리뷰에서 별점, 작성 날짜, 리뷰 내용을 추출
        - 중복 리뷰를 제거하여 최소 500개의 리뷰를 self.reviews 리스트에 저장
        """


        options = Options()
        options.add_argument("--start-maximized")  # 창 크게
        # options.add_argument("--headless=new")   # 창 안 띄우고 실행

        self.driver = webdriver.Chrome(options=options)

    

    def scrape_reviews(self):
            """
            카카오맵 장소 페이지에서 리뷰를 크롤링하는 메서드

            - 카카오맵이 사진 탭으로 이동하는 문제를 방지하기 위해
            후기(리뷰) 화면으로 강제 전환
            - 스크롤을 통해 동적으로 로딩되는 리뷰를 반복적으로 수집
            - 각 리뷰에서 별점, 작성 날짜, 리뷰 내용을 추출
            - 중복 리뷰를 제거하여 최소 500개의 리뷰를 self.reviews 리스트에 저장
            """

            # 0) 브라우저 열기
            self.start_browser()
            wait = WebDriverWait(self.driver, 12)

            # 1) "사진(#photoview)"으로 튀면 "후기(#comment)"로 되돌리기
            def ensure_review_view():
                for _ in range(10):  # 10번까지 되돌리기 시도
                    # URL이나 상태 체크 (간단한 체크 추가)
                    if "comment" in self.driver.current_url and self.driver.find_elements(By.CSS_SELECTOR, "ul.list_review > li"):
                        return True

                    self.driver.get("https://place.map.kakao.com/27560699")
                    time.sleep(1.5)

                    # 해시를 강제로 후기(comment)로
                    self.driver.execute_script("location.hash='comment';")
                    time.sleep(1.0)

                    # 탭 텍스트로 후기/리뷰 클릭(보험)
                    try:
                        tab = self.driver.find_element(By.XPATH, "//a[contains(.,'후기') or contains(.,'리뷰')]")
                        self.driver.execute_script("arguments[0].click();", tab)
                        time.sleep(1.0)
                    except:
                        pass

                    # 진짜 리뷰 li가 뜨면 성공
                    try:
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.list_review > li")))
                        return True
                    except TimeoutException:
                        # 아직도 사진이면 다시 시도 (카카오가 튕기는 케이스)
                        continue
                return False

            ok = ensure_review_view()
            if not ok:
                logger.error(" 계속 사진 탭으로 튀어서 리뷰 화면을 고정하지 못했습니다.")
                time.sleep(5)  # 바로 꺼져서 확인 못하는 것 방지
                self.driver.quit()
                return

            REVIEW_CARD = "ul.list_review > li"

            # 2) 스크롤 컨테이너 찾기
            scroll_container = self.driver.execute_script("""
                const ul = document.querySelector('ul.list_review');
                if (!ul) return document.scrollingElement;
                let p = ul.parentElement;
                while (p) {
                    const s = getComputedStyle(p);
                    const canScroll = (p.scrollHeight > p.clientHeight) &&
                                    (s.overflowY === 'auto' || s.overflowY === 'scroll');
                    if (canScroll) return p;
                    p = p.parentElement;
                }
                return document.scrollingElement;
            """)

            # 3) 스크롤 (Data Loading Phase) - 여기서는 파싱하지 않고 로딩만 함
            TARGET = 500
            no_grow = 0
            last_count = 0

            logger.info("스크롤 시작: 리뷰 로딩 중...")

            while True:
                # 현재 로딩된 카드 개수 확인 (텍스트 추출 X -> 속도 빠름)
                cards = self.driver.find_elements(By.CSS_SELECTOR, REVIEW_CARD)
                current_count = len(cards)
                
                # 목표 달성 시 중단
                if current_count >= TARGET:
                    logger.info(f"목표 수량 도달: {current_count}/{TARGET}")
                    break
                
                # 더 이상 로딩이 안 되면(20번 시도) 중단
                if current_count == last_count:
                    no_grow += 1
                else:
                    no_grow = 0
                
                if no_grow >= 20:
                    logger.info("더 이상 리뷰가 로드되지 않습니다.")
                    break

                last_count = current_count

                # 4) 스크롤 + 새 카드 증가 대기
                self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scroll_container)
                
                try:
                    WebDriverWait(self.driver, 3).until(
                        lambda d: len(d.find_elements(By.CSS_SELECTOR, REVIEW_CARD)) > current_count
                    )
                except TimeoutException:
                    time.sleep(0.5) # 타임아웃 나도 일단 루프는 계속 돔 (네트워크 지연 대비)

            # (Optional) '더보기' 버튼 일괄 클릭 (긴 리뷰 전개)
            try:
                self.driver.execute_script("""
                    document.querySelectorAll('button.btn_more, a.link_more').forEach(b => b.click());
                """)
                time.sleep(1.5)
            except:
                pass

            # 5) BeautifulSoup으로 일괄 파싱 (Batch Parsing Phase)
            logger.info(f"HTML 파싱 시작: 총 {last_count}개 항목 처리 중...")
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            review_items = soup.select(REVIEW_CARD)
            
            seen = set()

            for card in review_items:
                if len(self.reviews) >= TARGET:
                    break

                # 날짜
                date_text = ""
                for sel in ["span.time_write", "span.txt_date", ".date"]:
                    elem = card.select_one(sel)
                    if elem:
                        date_text = elem.get_text(strip=True)
                        if date_text: break
                
                # 내용
                content_text = ""
                for sel in ["p.txt_comment", "p.desc_review", ".review_desc", "span.txt_comment"]:
                    elem = card.select_one(sel)
                    if elem:
                        content_text = elem.get_text(strip=True)
                        if content_text: break

                if not date_text or not content_text:
                    continue

                # 별점(없으면 N/A)
                rating_text = "N/A"
                for sel in ["em.num_rate", "span.score_star", "span.starred_grade"]:
                    elem = card.select_one(sel)
                    if elem:
                        # textContent 혹은 aria-label 등에서 숫자 추출
                        raw = elem.get_text(strip=True)
                        m = re.search(r"(\d+(\.\d+)?)", raw)
                        if m:
                            rating_text = m.group(1)
                            break

                # 중복 제거
                key = f"{date_text}|{content_text[:80]}"
                if key in seen:
                    continue
                seen.add(key)

                self.reviews.append({"rating": rating_text, "date": date_text, "content": content_text})

            logger.info(f" 수집 완료: {len(self.reviews)}개")
            self.driver.quit()

    def save_to_database(self):
        """
        수집한 리뷰(self.reviews)를 CSV로 저장하는 역할
        - self.reviews에 저장된 리뷰 목록을 pandas DataFrame으로 변환한다.
        - output_dir 하위에 database 폴더를 생성(존재하지 않을 경우)한다.
        - 리뷰 데이터를 reviews_kakao.csv 파일로 저장한다.
        - 저장되는 CSV 파일은 rating, date, content 컬럼을 가진다.
        """
        
        # 저장할 CSV 파일의 전체 경로
        out_path = os.path.join(self.output_dir, "reviews_kakao.csv") 

        # self.reviews(리스트) -> 데이터프레임
        df = pd.DataFrame(self.reviews)  
        df = df[["rating", "date", "content"]]  # 컬럼 순서대로. 필수 3개만.

        # csv 저장
        df.to_csv(out_path, index=False, encoding="utf-8-sig")
        logger.info(f"Kakao reviews saved to: {out_path}")  # 어디에 저장됐는지 로그로 남김

