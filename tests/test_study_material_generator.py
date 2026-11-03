
import pytest
from unittest.mock import MagicMock

from src.llm.study_material_generator import StudyMaterialGenerator


@pytest.fixture
def generator():
    client = MagicMock()
    return StudyMaterialGenerator(client=client)


@pytest.fixture
def pdf_context():
    return """
    [Page 1]
    Mars is called the Red Planet because iron minerals in its soil
    give it a reddish appearance.
    Mars has two moons: Phobos and Deimos.
    A Martian day lasts approximately 24 hours and 37 minutes.
    """


def test_quiz_generation(generator, pdf_context):
    generator._request_json = MagicMock(return_value={
        "questions": [{
            "question": "Why is Mars called the Red Planet?",
            "options": {
                "A": "Iron minerals give it a reddish appearance",
                "B": "It is very hot",
                "C": "It has two moons",
                "D": "It is the largest planet"
            },
            "correct_answer": "A",
            "explanation": "Iron minerals give Mars its reddish appearance.",
            "page_number": 1
        }]
    })

    result = generator.generate_quiz(pdf_context, 1)

    assert len(result) == 1
    assert result[0]["correct_answer"] == "A"
    assert result[0]["page_number"] == 1


def test_flashcard_generation(generator, pdf_context):
    generator._request_json = MagicMock(return_value={
        "flashcards": [{
            "front": "Why is Mars called the Red Planet?",
            "back": "Iron minerals give its soil a reddish appearance.",
            "page_number": 1
        }]
    })

    result = generator.generate_flashcards(pdf_context, 1)

    assert len(result) == 1
    assert result[0]["page_number"] == 1


def test_empty_context_rejected(generator):
    with pytest.raises(ValueError):
        generator.generate_quiz("", 1)


def test_invalid_question_count_rejected(generator, pdf_context):
    with pytest.raises(ValueError):
        generator.generate_quiz(pdf_context, 0)


def test_invalid_page_number_rejected(generator, pdf_context):
    generator._request_json = MagicMock(return_value={
        "flashcards": [{
            "front": "What are Mars's moons?",
            "back": "Phobos and Deimos.",
            "page_number": 99
        }]
    })

    with pytest.raises(ValueError):
        generator.generate_flashcards(pdf_context, 1)
