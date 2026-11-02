"""Prompt templates used by EduPulse AI."""

SYSTEM_PROMPT = (
    "Answer using only the provided PDF context. "
    "If the answer is not supported by the context, "
    "say you cannot find it in the document. "
    "Cite sources using the exact format [Page N]."
)


def build_user_prompt(context: str, question: str) -> str:
    """Build the user message containing PDF context and question."""
    return f"PDF context:\n{context}\n\nQuestion: {question}"