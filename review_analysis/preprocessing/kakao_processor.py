# @chu20-afk
from .base_processor import BaseDataProcessor
from utils.logger import setup_logger
import pandas as pd
import re
import os

logger = setup_logger(__name__)


class KakaoProcessor(BaseDataProcessor):
    """
    Processor for Kakao Map reviews data.

    Input CSV columns (expected):
    - rating
    - date
    - content
    """

    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.df: pd.DataFrame | None = None
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
        Performs data cleaning:
        1) Null value processing
        2) Type normalization (rating/date)
        3) Abnormal value processing
        4) Text preprocessing (content)
        5) Deduplication
        """
        logger.info("Starting preprocessing...")
        if self.df is None:
            self.load_data()

        if self.df is None or self.df.empty:
            logger.warning("DataFrame is empty. Skipping preprocessing.")
            return

        # 0) 필요한 컬럼 존재 확인
        required_cols = ["rating", "date", "content"]
        missing = [c for c in required_cols if c not in self.df.columns]
        if missing:
            logger.error(f"Missing required columns: {missing}")
            self.df = pd.DataFrame()
            return

        initial_count = len(self.df)

        # 1) Null/빈문자 처리
        self.df = self.df.replace({"": pd.NA, "None": pd.NA, "none": pd.NA, "nan": pd.NA})
        self.df.dropna(subset=required_cols, inplace=True)

        # 2) 타입 정리: rating -> numeric, date -> datetime
        self.df["rating"] = pd.to_numeric(self.df["rating"], errors="coerce")
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

        # rating/date 변환 실패한 행 제거
        self.df.dropna(subset=["rating", "date"], inplace=True)

        # 3) 이상치 처리: rating 1~5만 유지
        before_abnormal = len(self.df)
        self.df = self.df[(self.df["rating"] >= 1) & (self.df["rating"] <= 5)]
        logger.info(f"Dropped {before_abnormal - len(self.df)} rows with abnormal rating.")

        # 4) 텍스트 전처리(content)
        def clean_text(text: object) -> str:
            if not isinstance(text, str):
                return ""
            text = re.sub(r"\s+", " ", text).strip()
            # 카카오 리뷰에서 종종 보이는 '... 더보기' 제거
            text = text.replace("... 더보기", "").strip()
            return text

        self.df["content"] = self.df["content"].apply(clean_text)

        # content가 너무 짧으면 제거(의미 없는/깨진 데이터 방지)
        before_short = len(self.df)
        self.df = self.df[self.df["content"].str.len() >= 2]
        logger.info(f"Dropped {before_short - len(self.df)} rows with too-short content.")

        # 5) 중복 제거(같은 날짜 + 같은 내용은 같은 리뷰로 간주)
        before_dup = len(self.df)
        self.df.drop_duplicates(subset=["date", "content"], inplace=True)
        logger.info(f"Dropped {before_dup - len(self.df)} duplicate rows.")

        logger.info(f"Preprocessing done. {initial_count} -> {len(self.df)} rows.")

    def feature_engineering(self):
        """
        Generates additional parameters:
        - review_length: length of review text
        - is_positive: 1 if rating >= 4 else 0
        """
        logger.info("Starting feature engineering...")
        if self.df is None or self.df.empty:
            logger.warning("DataFrame is empty. Skipping feature engineering.")
            return

        self.df["review_length"] = self.df["content"].apply(len)
        self.df["is_positive"] = (self.df["rating"] >= 4).astype(int)

        logger.info("Feature engineering completed. Added 'review_length' and 'is_positive'.")

    def save_to_database(self):
        """Saves the processed data to the output directory."""
        logger.info("Saving processed data...")
        if self.df is None or self.df.empty:
            logger.warning("No data to save.")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = f"{base_name}_processed.csv"
        output_file = os.path.join(self.output_dir, output_filename)

        try:
            self.df.to_csv(output_file, index=False, encoding="utf-8-sig")
            logger.info(f"Successfully saved processed data to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save processed data: {e}")
