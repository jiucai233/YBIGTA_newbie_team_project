# @jiucai233
from .base_processor import BaseDataProcessor
from utils.logger import setup_logger
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
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            # Optionally remove special characters if needed, 
            # but for now we keep punctuation as it might be useful.
            return text

        self.df['review'] = self.df['review'].apply(clean_text)
        logger.info("Text data preprocessing completed.")

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
        
        logger.info("Feature engineering completed. Added 'review_length' and 'is_positive'.")

    def save_to_database(self):
        """Saves the processed data to the output directory."""
        logger.info("Saving processed data...")
        if self.df is None or self.df.empty:
            logger.warning("No data to save.")
            return

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # Append '_processed' to the filename
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = f"{base_name}_processed.csv"
        output_file = os.path.join(self.output_dir, output_filename)

        try:
            self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
            logger.info(f"Successfully saved processed data to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save processed data: {e}")
