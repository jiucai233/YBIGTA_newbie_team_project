import os
import pickle
import numpy as np
import faiss as faiss_lib
import pandas as pd
from langchain_upstage import UpstageEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FAISS_INDEX_DIR = os.path.join(BASE_DIR, "st_app", "db", "faiss_index")
DB_DIR = os.path.join(BASE_DIR, "database")

REVIEW_FILES = [
    ("preprocessed_reviews_google.csv", "google"),
    ("preprocessed_reviews_tripdotcom.csv", "tripdotcom"),
    ("preprocessed_reviews_kakao.csv", "kakao"),
]


def _get_embeddings() -> UpstageEmbeddings:
    return UpstageEmbeddings(model="solar-embedding-1-large")


def load_reviews() -> list[Document]:
    """Load preprocessed review CSVs and convert to LangChain Documents."""
    docs: list[Document] = []
    for filename, source in REVIEW_FILES:
        filepath = os.path.join(DB_DIR, filename)
        if not os.path.exists(filepath):
            continue
        df = pd.read_csv(filepath)
        for _, row in df.iterrows():
            content = str(row.get("content", "")).strip()
            if not content or content == "nan":
                continue
            metadata = {
                "source": source,
                "rating": str(row.get("rating", "")),
                "date": str(row.get("date", "")),
            }
            docs.append(Document(page_content=content, metadata=metadata))
    return docs


def _save_faiss_local(vectorstore: FAISS, folder: str) -> None:
    """Save FAISS index using Python I/O to avoid C++ Unicode path issues on Windows."""
    os.makedirs(folder, exist_ok=True)
    # Serialize FAISS index to bytes via numpy, then write with Python (handles Unicode paths)
    index_array = faiss_lib.serialize_index(vectorstore.index)
    with open(os.path.join(folder, "index.faiss"), "wb") as f:
        f.write(index_array.tobytes())
    # Save docstore and mapping via pickle
    with open(os.path.join(folder, "index.pkl"), "wb") as f:
        pickle.dump(
            (vectorstore.docstore, vectorstore.index_to_docstore_id), f
        )


def _load_faiss_local(folder: str, embeddings) -> FAISS:
    """Load FAISS index using Python I/O to avoid C++ Unicode path issues on Windows."""
    with open(os.path.join(folder, "index.faiss"), "rb") as f:
        index_array = np.frombuffer(f.read(), dtype=np.uint8)
    index = faiss_lib.deserialize_index(index_array)
    with open(os.path.join(folder, "index.pkl"), "rb") as f:
        docstore, index_to_docstore_id = pickle.load(f)
    return FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )


def build_faiss_index() -> FAISS:
    """Build FAISS index from all preprocessed review data and save to disk."""
    embeddings = _get_embeddings()
    docs = load_reviews()
    print(f"Building FAISS index from {len(docs)} review documents...")
    vectorstore = FAISS.from_documents(docs, embeddings)
    _save_faiss_local(vectorstore, FAISS_INDEX_DIR)
    print(f"FAISS index saved to {FAISS_INDEX_DIR}")
    return vectorstore


def load_faiss_index() -> FAISS:
    """Load existing FAISS index, or build one if it doesn't exist."""
    embeddings = _get_embeddings()
    index_path = os.path.join(FAISS_INDEX_DIR, "index.faiss")
    if os.path.exists(index_path):
        return _load_faiss_local(FAISS_INDEX_DIR, embeddings)
    return build_faiss_index()


if __name__ == "__main__":
    build_faiss_index()
