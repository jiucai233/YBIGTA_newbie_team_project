# @jiucai233
from .base_processor import BaseDataProcessor
from utils.logger import setup_logger
from utils.tfidf import tfidf_embedding
import pandas as pd
import re
import os

logger = setup_logger(__name__)
class GoogleProcessor(BaseDataProcessor):
    """
    Processor for Google Maps reviews data.
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
        self.df.dropna(subset=['review', 'stars', 'date'], inplace=True)
        logger.info(f"Dropped {initial_count - len(self.df)} rows containing null values.")
        
        # 2. Abnormal value process
        # Filter stars to be between 1 and 5
        before_abnormal = len(self.df)
        self.df = self.df[(self.df['stars'] >= 1) & (self.df['stars'] <= 5)]
        logger.info(f"Dropped {before_abnormal - len(self.df)} rows with abnormal star ratings.")

        # 3. Text data preprocessing
        # Function to clean text
        def clean_text(text):
            if not isinstance(text, str):
                return ""
            # Remove Emojis
            text = self.remove_emojis(text)
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Optionally remove special characters if needed, 
            # but for now we keep punctuation as it might be useful.
            return text

        self.df['review'] = self.df['review'].apply(clean_text)
        logger.info("Text data preprocessing completed.")

    @staticmethod
    def remove_emojis(text: str) -> str:
        """
        Removes emojis from a string.
        """
        if not isinstance(text, str):
            return ""
        
        # Comprehensive regex to remove most emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)

    def feature_engineering(self):
        """
        Generates additional parameters:
        - review_length: Length of the review text.
        - is_positive: Boolean indicating if the review is positive (stars >= 4).
        """
        logger.info("Starting feature engineering...")
        if self.df is None or self.df.empty:
            logger.warning("DataFrame is empty. Skipping feature engineering.")
            return

        # Generate 'review_length'
        self.df['review_length'] = self.df['review'].apply(len)
        
        # Generate 'is_positive' (Binary sentiment based on stars)
        # 4-5 stars: Positive (1), 1-3 stars: Negative/Neutral (0) - simple heuristic
        self.df['is_positive'] = (self.df['stars'] >= 4).astype(int)
        
        self.generate_text_embeddings()
        logger.info("Feature engineering completed. Added 'review_length' and 'is_positive'.")

    def generate_text_embeddings(self):
        """
        Generates TF-IDF embeddings for the review text.
        """
        logger.info("Generating TF-IDF embeddings...")
        if self.df is None or self.df.empty or 'review' not in self.df.columns:
            logger.warning("DataFrame is empty or 'review' column is missing. Skipping TF-IDF generation.")
            return

        # Ensure all reviews are strings
        reviews = self.df['review'].astype(str).tolist()
        
        self.tfidf_embeddings = tfidf_embedding(reviews)
        logger.info(f"Generated TF-IDF embeddings with shape {self.tfidf_embeddings.shape}")

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
