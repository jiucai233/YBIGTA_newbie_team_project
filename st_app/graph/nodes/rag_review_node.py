from st_app.utils.state import GraphState
from st_app.rag.retriever import retrieve_reviews


def rag_review_node(state: GraphState) -> dict:
    """
    FAISS 벡터 DB 기반 리뷰 RAG 노드.
    사용자 질문과 유사한 리뷰를 검색하여 컨텍스트로 반환한다.
    이후 chat_node가 이 컨텍스트를 활용해 최종 답변을 생성한다.
    """
    print("---RAG REVIEW NODE---", flush=True)
    user_input = state["user_input"]

    docs = retrieve_reviews(user_input, k=5)

    if not docs:
        return {"review": "No relevant reviews found.", "context": ""}

    review_parts: list[str] = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        rating = doc.metadata.get("rating", "N/A")
        date = doc.metadata.get("date", "")
        header = f"[Review {i} | source: {source}, rating: {rating}, date: {date}]"
        review_parts.append(f"{header}\n{doc.page_content}")

    review_context = "\n\n".join(review_parts)
    return {"review": review_context, "context": review_context}
