"""Generate answers from retrieved PDF context using an LLM."""

from openai import OpenAI

from src.prompts.prompt_templates import SYSTEM_PROMPT, build_user_prompt


class AnswerGenerator:
    """Send retrieved context and a question to the configured chat model."""

    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-4o-mini",
    ) -> None:
        self.client = client
        self.model = model

    def generate(self, context: str, question: str) -> str:
        """Return an answer generated from the supplied PDF context."""
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": build_user_prompt(context, question),
                },
            ],
        )

        return response.choices[0].message.content or ""