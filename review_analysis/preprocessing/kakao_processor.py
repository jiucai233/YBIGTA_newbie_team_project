# @chu20-afk
import os
import re
import pandas as pd # type: ignore
from .base_processor import BaseDataProcessor
from utils.logger import setup_logger
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore

logger = setup_logger(__name__)


class KakaoProcessor(BaseDataProcessor):
    """
    Kakao reviews processor.

    Flow:
    1) load_data(): CSV 로드
    2) preprocess(): 결측치/이상치 제거 + 텍스트 전처리(이모지/특수문자 제거)
    3) feature_engineering(): content_length, is_positive + TF-IDF 임베딩 생성
    4) save_to_database(): preprocessed_{원본파일명}.csv 및 {원본파일명}_tfidf_embeddings.csv 저장
    """

    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.df = None
        self.tfidf_embeddings = None
        logger.info(f"KakaoProcessor initialized with input: {input_path}")

    def load_data(self):
        """Loads data from the CSV file."""
        if os.path.exists(self.input_path):
            try:
                self.df = pd.read_csv(self.input_path)
                logger.info(f"Loaded {len(self.df)} rows from {self.input_path}")
            except Exception as e:
                logger.error(f"Failed to load data: {e}")
                self.df = pd.DataFrame()
        else:
            logger.error(f"Input file not found: {self.input_path}")
            self.df = pd.DataFrame()

    def preprocess(self):
        """
        데이터 정제:
        1) 결측치 제거: content, rating, date 중 하나라도 없으면 제거
        2) 이상치 제거: rating 1~5 범위 밖 제거
        3) 텍스트 전처리: 이모지/특수문자 제거 후 공백 정리 (한글/영문/숫자/공백만 남김)
        """
        logger.info("[Kakao] Starting preprocessing...")
        if self.df is None:
            self.load_data()

        if self.df.empty:
            logger.warning("[Kakao] DataFrame is empty. Skipping preprocessing.")
            return

        # 1) Null value processing
        initial_count = len(self.df)
        self.df.dropna(subset=["content", "rating", "date"], inplace=True)
        logger.info(f"[Kakao] Dropped {initial_count - len(self.df)} rows containing null values.")

        # 2) Abnormal value processing
        before_abnormal = len(self.df)
        self.df = self.df[(self.df["rating"] >= 1) & (self.df["rating"] <= 5)]
        logger.info(f"[Kakao] Dropped {before_abnormal - len(self.df)} rows with abnormal star ratings.")

        # 3) Text preprocessing (emoji/special chars remove)
        def clean_text(text) -> str:
            """
            이모지/특수문자 제거 + 공백 정리
            - 한글/영문/숫자/공백만 남김
            """
            if not isinstance(text, str):
                return ""
            text = re.sub(r"[^가-힣a-zA-Z0-9\s]", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            # '...더보기' 제거
            text = re.sub(r"\.\.\.더보기", "", text).strip()

            return text

        self.df["content"] = self.df["content"].apply(clean_text)
        logger.info("[Kakao] Text preprocessing completed.")

    def feature_engineering(self):
        """
        파생변수 + TF-IDF 임베딩 생성:
        - content_length: content 길이
        - is_positive: rating >= 4 이면 1, 아니면 0
        - tfidf_embeddings: content 기반 TF-IDF 벡터
        """
        logger.info("[Kakao] Starting feature engineering...")
        if self.df is None or self.df.empty:
            logger.warning("[Kakao] DataFrame is empty. Skipping feature engineering.")
            return

        # content_length
        self.df["content_length"] = self.df["content"].astype(str).apply(len)

        # is_positive
        self.df["is_positive"] = (self.df["rating"] >= 4).astype(int)

        # TF-IDF embeddings
        logger.info("[Kakao] Generating TF-IDF embeddings...")
        if "content" not in self.df.columns:
            logger.warning("[Kakao] 'content' column is missing. Skipping TF-IDF generation.")
            return

        contents = self.df["content"].astype(str).tolist()
        vectorizer = TfidfVectorizer(max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(contents)

        self.tfidf_embeddings = pd.DataFrame(
            tfidf_matrix.toarray(),
            columns=vectorizer.get_feature_names_out(),
        )

        logger.info(f"[Kakao] Generated TF-IDF embeddings with shape {self.tfidf_embeddings.shape}")
        logger.info("[Kakao] Feature engineering completed. Added 'content_length' and 'is_positive'.")

    def save_to_database(self):
        """Saves processed CSV and (optional) TF-IDF embeddings CSV."""
        logger.info("[Kakao] Saving processed data...")
        if self.df is None or self.df.empty:
            logger.warning("[Kakao] No data to save.")
            return

        os.makedirs(self.output_dir, exist_ok=True)

        # preprocessed_{원본파일명}.csv
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = f"preprocessed_{base_name}.csv"
        output_file = os.path.join(self.output_dir, output_filename)

        try:
            self.df.to_csv(output_file, index=False, encoding="utf-8-sig")
            logger.info(f"[Kakao] Successfully saved processed data to {output_file}")
        except Exception as e:
            logger.error(f"[Kakao] Failed to save processed data: {e}")

        # TF-IDF 임베딩도 저장 (구글과 동일한 규칙)
        if self.tfidf_embeddings is not None:
            tfidf_output_filename = f"{base_name}_tfidf_embeddings.csv"
            tfidf_output_file = os.path.join(self.output_dir, tfidf_output_filename)
            try:
                self.tfidf_embeddings.to_csv(tfidf_output_file, index=False, encoding="utf-8-sig")
                logger.info(f"[Kakao] Successfully saved TF-IDF embeddings to {tfidf_output_file}")
            except Exception as e:
                logger.error(f"[Kakao] Failed to save TF-IDF embeddings: {e}")
