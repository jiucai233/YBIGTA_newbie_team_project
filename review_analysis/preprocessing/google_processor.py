# @jiucai233
from .base_processor import BaseDataProcessor
from utils.logger import setup_logger
from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore
import pandas as pd # type: ignore
import re
import os

logger = setup_logger(__name__)
class GoogleProcessor(BaseDataProcessor):
    """
    Processor for Google Maps contents data.
    """
    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.df = None
        self.tfidf_embeddings = None
        logger.info(f"GoogleProcessor initialized with input: {input_path}")

    def load_data(self):
        """Loads data from the CSV file."""
        if os.path.exists(self.input_path):
            try:
                self.df = pd.read_csv(self.input_path)
                logger.info(f"Loaded {len(self.df)} rows from {self.input_path}")
            except Exception as e:
                logger.error(f"Failed to load data: {e}")
                self.df = pd.DataFrame() # Empty fallback
        else:
            logger.error(f"Input file not found: {self.input_path}")
            self.df = pd.DataFrame()

    def preprocess(self):
        """
        Performs data cleaning:
        1. Null value processing
        2. Abnormal value processing
        3. Text data preprocessing
        """
        logger.info("Starting preprocessing...")
        if self.df is None:
            self.load_data()
        
        if self.df.empty:
            logger.warning("DataFrame is empty. Skipping preprocessing.")
            return

        initial_count = len(self.df)

        # 1. Null value process
        self.df.dropna(subset=['content', 'rating', 'date'], inplace=True)
        logger.info(f"Dropped {initial_count - len(self.df)} rows containing null values.")
        
        # 2. Abnormal value process
        # Filter rating to be between 1 and 5
        before_abnormal = len(self.df)
        self.df = self.df[(self.df['rating'] >= 1) & (self.df['rating'] <= 5)]
        logger.info(f"Dropped {before_abnormal - len(self.df)} rows with abnormal star ratings.")

        # 3. Text data preprocessing
        # Function to clean text
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
        logger.info("Text data preprocessing completed.")

    def feature_engineering(self):
        """
        Generates additional parameters:
        - content_length: Length of the content text.
        - is_positive: Boolean indicating if the content is positive (rating >= 4).
        and also generates TF-IDF embeddings for the content text.
        """
        logger.info("Starting feature engineering...")
        if self.df is None or self.df.empty:
            logger.warning("DataFrame is empty. Skipping feature engineering.")
            return

        # Generate 'content_length'
        self.df['content_length'] = self.df['content'].apply(len)
        
        # Generate 'is_positive' (Binary sentiment based on rating)
        # 4-5 rating: Positive (1), 1-3 rating: Negative/Neutral (0) - simple heuristic
        self.df['is_positive'] = (self.df['rating'] >= 4).astype(int)

        # Generate TF-IDF embeddings for the content text.
        logger.info("Generating TF-IDF embeddings...")
        if self.df is None or self.df.empty or 'content' not in self.df.columns:
            logger.warning("DataFrame is empty or 'content' column is missing. Skipping TF-IDF generation.")
            return

        # Ensure all contents are strings
        contents = self.df['content'].astype(str).tolist()

        vectorizer = TfidfVectorizer(max_features=5000)
        tfidf_matrix = vectorizer.fit_transform(contents)

        # Create a DataFrame from the TF-IDF matrix
        self.tfidf_embeddings = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        logger.info(f"Generated TF-IDF embeddings with shape {self.tfidf_embeddings.shape}")
        logger.info("Feature engineering completed. Added 'content_length' and 'is_positive'.")




    def save_to_database(self):
        """Saves the processed data and TF-IDF embeddings to the output directory."""
        logger.info("Saving processed data...")
        if self.df is None or self.df.empty:
            logger.warning("No data to save.")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Append 'preprocessed' to the filename
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = f"preprocessed_{base_name}.csv"
        output_file = os.path.join(self.output_dir, output_filename)

        try:
            self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"Successfully saved processed data to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save processed data: {e}")

        if self.tfidf_embeddings is not None:
            tfidf_output_filename = f"{base_name}_tfidf_embeddings.csv"
            tfidf_output_file = os.path.join(self.output_dir, tfidf_output_filename)
            try:
                self.tfidf_embeddings.to_csv(tfidf_output_file, index=False, encoding='utf-8-sig')
                logger.info(f"Successfully saved TF-IDF embeddings to {tfidf_output_file}")
            except Exception as e:
                logger.error(f"Failed to save TF-IDF embeddings: {e}")
