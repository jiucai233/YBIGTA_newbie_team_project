import os
import pandas as pd
import re
from .base_processor import BaseDataProcessor
from utils.logger import setup_logger
from sklearn.feature_extraction.text import TfidfVectorizer

logger = setup_logger(__name__)

class TripdotcomProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.df = None
        logger.info(f"TripdotcomProcessor {input_path}에서 실행 중")

    def load_data(self):
        """csv 파일에서 데이터를 로드합니다."""
        if os.path.exists(self.input_path):
            try:
                self.df = pd.read_csv(self.input_path)
                logger.info(f"Successfully loaded {len(self.df)} rows.")
            except Exception as e:
                logger.error(f"Failed to load data: {e}")
                self.df = pd.DataFrame()
        else:
            logger.error(f"Input file not found: {self.input_path}")
            self.df = pd.DataFrame()

    def preprocess(self):
        """
        결측치 및 이상치 처리, 텍스트 전처리를 수행합니다.
        1. 결측치: 결측치가 있는 행 제거
        2. 이상치: rating이 1~5 범위를 벗어나는 행 제거
        3. 텍스트 전처리: 특수문자 제거, 불필요한 공백 제거 등
        """
        logger.info("전처리 시작...")
        if self.df is None:
            self.load_data()
        
        if self.df.empty:
            logger.warning("데이터프레임이 비어있어 전처리를 건너뜁니다.")
            return

        initial_count = len(self.df)
        self.df.dropna(subset=['rating', 'content', 'date'], inplace=True)
        logger.info(f"{initial_count - len(self.df)}개의 결측치 제거")

        before_outlier = len(self.df)
        self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]
        logger.info(f"Removed {before_outlier - len(self.df)} rows with invalid ratings.")

        def clean_text(text) -> str:
            """
            리뷰 텍스트를 전처리합니다.
            이모지 및 특수문자 제거 후 텍스트 벡터화를 진행합니다.

            Args:
                text (str): 원본 리뷰 텍스트

            Returns:
                str: 전처리된 리뷰 텍스트
            """
            if not isinstance(text, str): return ""
            # 이모지 및 특수문자 제거, 한글/영문/숫자만 남김
            text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
            # 연속된 공백 하나로 축소
            text = re.sub(r'\s+', ' ', text).strip()
            return text

        self.df['content'] = self.df['content'].apply(clean_text)
        logger.info("Text preprocessing completed.")

    def feature_engineering(self):
        """
        분석을 위한 파생 변수를 생성합니다.
        1. content_length: 리뷰 텍스트 길이
        2. month: 시계열 분석을 위한 '월' 정보
        3. is_weekend: 주말 여부 (요일 기반)
        """
        logger.info("파생 변수 생성 시작...")
        if self.df is None or self.df.empty: return

        # 날짜 형식 변환
        self.df['date'] = pd.to_datetime(self.df['date'])

        # 텍스트 길이
        self.df['content_length'] = self.df['content'].apply(len)

        # 월 추출
        self.df['month'] = self.df['date'].dt.month

        # 요일 정보
        self.df['weekday'] = self.df['date'].dt.day_name()

        contents = self.df['content'].astype(str).tolist()

        vectorizer = TfidfVectorizer(max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(contents)

        # Create a DataFrame from the TF-IDF matrix
        self.tfidf_embeddings = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        logger.info(f"Generated TF-IDF embeddings with shape {self.tfidf_embeddings.shape}")

    def save_to_database(self):
        """
        전처리된 데이터를 CSV 파일로 저장합니다.
        """
        if self.df is None or self.df.empty: return

        output_file = os.path.join(self.output_dir, "preprocessed_reviews_tripdotcom.csv")

        try:
            self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"성공적으로 저장됨: {output_file}")
        except Exception as e:
            logger.error(f"저장 실패: {e}")

        if self.tfidf_embeddings is not None:
            tfidf_output_filename = f"reviews_tripdotcom_tfidf_embeddings.csv"
            tfidf_output_file = os.path.join(self.output_dir, tfidf_output_filename)
            try:
                self.tfidf_embeddings.to_csv(tfidf_output_file, index=False, encoding='utf-8-sig')
                logger.info(f"Successfully saved TF-IDF embeddings to {tfidf_output_file}")
            except Exception as e:
                logger.error(f"Failed to save TF-IDF embeddings: {e}")