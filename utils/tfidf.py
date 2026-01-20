# @jiucai233
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
import pandas as pd

def tfidf_embedding(texts: List[str], max_features: int = 5000) -> pd.DataFrame:
    """
    Generates TF-IDF embeddings for a list of texts.
    
    Args:
        texts (List[str]): A list of documents.
        max_features (int): The maximum number of features to keep.
        
    Returns:
        pd.DataFrame: A DataFrame where each row is the TF-IDF vector for a document.
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    # Create a DataFrame from the TF-IDF matrix
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    
    return tfidf_df
