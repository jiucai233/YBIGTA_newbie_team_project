from langchain_upstage import ChatUpstage
from langchain_core.messages import SystemMessage

from st_app.utils.state import GraphState


def chat_node(state: GraphState) -> dict:
    """
    최종 응답 생성 노드.
    앞단 노드에서 수집한 context(review/subject/analysis)를 시스템 지침에 넣고
    chat_history를 바탕으로 답변을 생성한다.
    """
    print("---CHAT NODE---")

    llm = ChatUpstage()

    review_context = state.get("review", "")
    subject_context = state.get("subject", "")
    analysis_context = state.get("analysis_result", "")

    context_parts: list[str] = []
    if review_context and "placeholder" not in review_context.lower():
        context_parts.append(f"[Review Information]\n{review_context}")
    if subject_context and "placeholder" not in subject_context.lower():
        context_parts.append(f"[Subject Information]\n{subject_context}")
    if analysis_context and "placeholder" not in analysis_context.lower():
        context_parts.append(f"[Data Analysis Result]\n{analysis_context}")

    messages = list(state.get("chat_history", []))

    if context_parts:
        system_prompt = (
            "You are a helpful Lotte World assistant. "
            "Use the provided context when relevant, avoid fabricating facts, "
            "and answer in a clear way.\n\n"
            + "\n\n".join(context_parts)
        )
        messages = [SystemMessage(content=system_prompt)] + messages

    response = llm.invoke(messages)
    return {"chat_history": [response]}
