from unittest.mock import Mock

from src.llm.answer_generator import AnswerGenerator


def test_generate_sends_prompts_and_returns_answer():
    client = Mock()
    client.chat.completions.create.return_value = Mock(
        choices=[
            Mock(
                message=Mock(content="The document says the deadline is Friday.")
            )
        ]
    )

    generator = AnswerGenerator(client=client, model="test-model")

    answer = generator.generate(
        context="[Page 2]\nThe deadline is Friday.",
        question="What is the deadline?",
    )

    assert answer == "The document says the deadline is Friday."

    client.chat.completions.create.assert_called_once()
    call_kwargs = client.chat.completions.create.call_args.kwargs

    assert call_kwargs["model"] == "test-model"
    assert call_kwargs["messages"][0]["role"] == "system"
    assert call_kwargs["messages"][1]["role"] == "user"
    assert "The deadline is Friday." in call_kwargs["messages"][1]["content"]
    assert "What is the deadline?" in call_kwargs["messages"][1]["content"]