"""EduPulse AI — PDF chat, quiz, and flashcards."""

import streamlit as st

from src.rag_pipeline import RAGPipeline


st.set_page_config(
    page_title="EduPulse AI",
    page_icon="📚",
    layout="centered",
)

st.title("📚 EduPulse AI")
st.caption("Ask questions and study using your PDF documents.")

# Initialize session state.
DEFAULTS = {
    "pipeline": None,
    "document_id": None,
    "document_name": None,
    "quiz": [],
    "quiz_answers": {},
    "quiz_submitted": False,
    "flashcards": [],
    "flashcard_index": 0,
    "flashcard_revealed": False,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


with st.sidebar:
    st.header("Upload your PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        accept_multiple_files=False,
        help="Select a PDF document to ask questions about.",
    )

    if uploaded_file is not None:
        st.write("File received:", uploaded_file.name)
        st.write("Size:", f"{uploaded_file.size:,} bytes")

        if st.button("Process PDF", type="primary"):
            try:
                with st.spinner("Processing your PDF..."):
                    pdf_bytes = uploaded_file.getvalue()
                    pipeline = RAGPipeline()
                    document_id = pipeline.index_pdf(pdf_bytes)

                    st.session_state["pipeline"] = pipeline
                    st.session_state["document_id"] = document_id
                    st.session_state["document_name"] = uploaded_file.name

                    # Clear study material from the previous PDF.
                    st.session_state["quiz"] = []
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_submitted"] = False
                    st.session_state["flashcards"] = []
                    st.session_state["flashcard_index"] = 0
                    st.session_state["flashcard_revealed"] = False

                st.success("PDF processed successfully!")

            except Exception as exc:
                st.error(f"Unable to process PDF: {exc}")

    if st.session_state["document_id"] is not None:
        st.caption("Active PDF document ID")
        st.code(st.session_state["document_id"])


if st.session_state["document_id"] is None:
    st.info("Upload a PDF and click Process PDF to get started.")
else:
    st.subheader(f"Study from {st.session_state['document_name']}")

    chat_tab, quiz_tab, flashcards_tab = st.tabs(
        ["💬 Chat", "📝 Quiz", "🗂️ Flashcards"]
    )

    with chat_tab:
        st.caption("Ask questions about the active PDF.")

        question = st.chat_input("Ask a question about your PDF...")

        if question:
            with st.chat_message("user"):
                st.write(question)

            with st.chat_message("assistant"):
                try:
                    with st.spinner("Finding an answer..."):
                        result = st.session_state["pipeline"].answer_question(
                            question=question,
                            document_id=st.session_state["document_id"],
                        )

                    st.write(result["answer"])

                    if result["sources"]:
                        with st.expander("View PDF sources"):
                            for source in result["sources"]:
                                st.markdown(
                                    f"**Page {source['page_number']}**"
                                )
                                st.write(source["text"])

                except Exception as exc:
                    st.error(f"Unable to answer question: {exc}")

    with quiz_tab:
        st.caption("Generate multiple-choice questions from the active PDF.")

        if st.button("Generate Quiz", key="generate_quiz", type="primary"):
            try:
                with st.spinner("Creating quiz from your PDF..."):
                    result = st.session_state["pipeline"].generate_quiz(
                        document_id=st.session_state["document_id"],
                        num_questions=5,
                    )

                st.session_state["quiz"] = result["questions"]
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False

                if result["message"]:
                    st.info(result["message"])
                elif not result["questions"]:
                    st.info(
                        "I couldn't find relevant information in this PDF."
                    )

            except Exception as exc:
                st.error(f"Unable to generate quiz: {exc}")

        quiz = st.session_state["quiz"]

        if quiz:
            with st.form("quiz_form"):
                for index, item in enumerate(quiz):
                    st.markdown(f"**{index + 1}. {item['question']}**")

                    options = item["options"]
                    choice = st.radio(
                        "Choose one answer:",
                        options=["A", "B", "C", "D"],
                        format_func=lambda key, opts=options: (
                            f"{key}. {opts[key]}"
                        ),
                        key=f"quiz_answer_{index}",
                        index=None,
                    )

                    st.session_state["quiz_answers"][index] = choice
                    st.caption(f"Source: Page {item['page_number']}")
                    st.divider()

                submitted = st.form_submit_button("Check Answers")

            if submitted:
                st.session_state["quiz_submitted"] = True

            if st.session_state["quiz_submitted"]:
                answers = st.session_state["quiz_answers"]
                score = sum(
                    answers.get(index) == item["correct_answer"]
                    for index, item in enumerate(quiz)
                )

                st.subheader(f"Your score: {score} / {len(quiz)}")

                for index, item in enumerate(quiz):
                    selected = answers.get(index)
                    correct = item["correct_answer"]

                    if selected == correct:
                        st.success(f"Question {index + 1}: Correct")
                    else:
                        st.error(
                            f"Question {index + 1}: "
                            f"Correct answer: {correct}. "
                            f"{item['options'][correct]}"
                        )

                    st.write(item["explanation"])
                    st.caption(f"Source: Page {item['page_number']}")

    with flashcards_tab:
        st.caption("Review key information from the active PDF.")

        if st.button(
            "Generate Flashcards",
            key="generate_flashcards",
            type="primary",
        ):
            try:
                with st.spinner("Creating flashcards from your PDF..."):
                    result = st.session_state[
                        "pipeline"
                    ].generate_flashcards(
                        document_id=st.session_state["document_id"],
                        num_cards=5,
                    )

                st.session_state["flashcards"] = result["flashcards"]
                st.session_state["flashcard_index"] = 0
                st.session_state["flashcard_revealed"] = False

                if result["message"]:
                    st.info(result["message"])
                elif not result["flashcards"]:
                    st.info(
                        "I couldn't find relevant information in this PDF."
                    )

            except Exception as exc:
                st.error(f"Unable to generate flashcards: {exc}")

        cards = st.session_state["flashcards"]

        if cards:
            index = st.session_state["flashcard_index"]
            card = cards[index]

            st.caption(f"Card {index + 1} of {len(cards)}")

            st.markdown(f"### {card['front']}")

            if st.session_state["flashcard_revealed"]:
                st.write(card["back"])
                st.caption(f"Source: Page {card['page_number']}")
            else:
                st.caption("Try to answer before revealing the back.")

            if st.button(
                "Hide Answer" if st.session_state["flashcard_revealed"]
                else "Reveal Answer",
                key="toggle_flashcard",
            ):
                st.session_state["flashcard_revealed"] = (
                    not st.session_state["flashcard_revealed"]
                )
                st.rerun()

            previous_col, next_col = st.columns(2)

            with previous_col:
                if st.button(
                    "← Previous",
                    disabled=index == 0,
                    key="previous_flashcard",
                ):
                    st.session_state["flashcard_index"] -= 1
                    st.session_state["flashcard_revealed"] = False
                    st.rerun()

            with next_col:
                if st.button(
                    "Next →",
                    disabled=index >= len(cards) - 1,
                    key="next_flashcard",
                ):
                    st.session_state["flashcard_index"] += 1
                    st.session_state["flashcard_revealed"] = False
                    st.rerun()