# @jiucai233
from typing import List, Dict, Any, Optional
from review_analysis.crawling.base_crawler import BaseCrawler
from utils.logger import setup_logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time
import os
import re
import dateparser

logger = setup_logger(__name__)
class GoogleCrawler(BaseCrawler):
    """
    A crawler for extracting reviews from Google Maps using Selenium and BeautifulSoup.
    
    Attributes:
        output_dir (str): Directory where the scraped data will be saved.
        url (str): The Google Maps URL for the target location.
        driver (Optional[webdriver.Chrome]): Selenium WebDriver instance.
        data (List[Dict[str, Any]]): List of dictionaries containing scraped review data.
    """

    def __init__(self, output_dir: str):
        """
        Initializes the GoogleCrawler.

        Args:
            output_dir (str): The directory to save the output CSV file.
        """
        super().__init__(output_dir)
        self.url: str = "https://www.google.com/maps/place/Lotte+World/data=!4m12!1m2!2m1!1sLotte+World!3m8!1s0x357ca5a7250efe81:0x433df2c1fec03b98!8m2!3d37.5111158!4d127.098167!9m1!1b1!15sCgtMb3R0ZSBXb3JsZCIDiAEBWg0iC2xvdHRlIHdvcmxkkgEKdGhlbWVfcGFya-ABAA!16zL20vMDNqbGo5?hl=en&entry=ttu&g_ep=EgoyMDI2MDExMy4wIKXMDSoKLDEwMDc5MjA3M0gBUAM%3D"
        self.driver: Optional[webdriver.Chrome] = None
        self.data: List[Dict[str, Any]] = []
        logger.info("GoogleCrawler initialized.")

    def start_browser(self) -> None:
        """
        Initializes and configures the Selenium Chrome WebDriver with specific options.
        """
        options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--lang=ko,en")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def scrape_reviews(self) -> None:
        """
        Navigates to Google Maps, handles infinite scrolling to load reviews, 
        and parses the page content using BeautifulSoup.
        """
        logger.info("Scraping reviews from Google Maps...")
        try:
            self.start_browser()
            if self.driver:
                self.driver.get(self.url)
                logger.info("Browser opened, refreshing page...")
                self.driver.refresh()
                time.sleep(2)  # Wait for page to reload
                
                wait = WebDriverWait(self.driver, 20)
                
                try:
                    scrollable_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))
                except Exception:
                    logger.warning("Could not find div[role='feed'], trying alternative selector...")
                    scrollable_div = self.driver.find_element(By.XPATH, "//div[contains(@class, 'm6QErb') and contains(@class, 'DxyBCb')]")

                last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                
                max_scrolls = 100
                last_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
                no_change_count = 0 

                for i in range(max_scrolls):
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                    time.sleep(2) 

                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

                    if new_height == last_height:
                        no_change_count += 1

                        if no_change_count >= 2:
                            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight - 300", scrollable_div)
                            time.sleep(1)
                            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                            time.sleep(1.5)
                            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

                            if new_height != last_height:
                                last_height = new_height
                                no_change_count = 0
                                continue 
                    else:
                        no_change_count = 0
                        last_height = new_height

                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                reviews = soup.find_all("div", class_="jftiEf")
                
                logger.info(f"Found {len(reviews)} reviews.")

                for review in reviews:
                    try:
                        star_elem = review.find("span", class_="kvMYJc")
                        stars = 0.0
                        if star_elem and star_elem.has_attr("aria-label"):
                            label = star_elem["aria-label"]
                            match = re.search(r"(\d+(\.\d+)?)", str(label))
                            if match:
                                stars = float(match.group(1))

                        date_elem = review.find("span", class_="rsqaWe")
                        date = date_elem.text.strip() if date_elem else ""
                        #change the date from "...ago" to "YYYY-MM-DD" format
                        dt = dateparser.parse(date, settings={'RELATIVE_BASE': datetime.now()})
                        date =  dt.strftime('%Y-%m-%d') if dt else None

                        content_elem = review.find("span", class_="wiI7pd")
                        content = content_elem.text.strip() if content_elem else ""
                        
                        self.data.append({
                            "rating": stars,
                            "date": date,
                            "content": content
                        })
                    except Exception as e:
                        logger.error(f"Error parsing a review: {e}")
                        continue

        except Exception as e:
            logger.error(f"An error occurred during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()

    def save_to_database(self) -> None:
        """
        Converts the collected data into a pandas DataFrame and exports it to a CSV file.
        """
        logger.info("Saving scraped reviews to database...")
        if not self.data:
            logger.warning("No data to save.")
            return

        try:
            df = pd.DataFrame(self.data)
            
            # Create output directory if it doesn't exist
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            output_file = os.path.join(self.output_dir, "reviews_google.csv")
            df.to_csv(output_file, index=False, encoding="utf-8-sig")
            logger.info(f"Successfully saved {len(df)} reviews to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save data: {e}")