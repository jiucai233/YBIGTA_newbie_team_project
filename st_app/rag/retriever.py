from langchain_core.documents import Document
from st_app.rag.embedder import load_faiss_index

_vectorstore = None


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_faiss_index()
    return _vectorstore


def retrieve_reviews(query: str, k: int = 5) -> list[Document]:
    """Retrieve the top-k most relevant review documents for a given query."""
    vectorstore = _get_vectorstore()
    return vectorstore.similarity_search(query, k=k)
