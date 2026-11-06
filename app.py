
"""EduPulse AI — PDF chat, quiz, and flashcards."""

from html import escape

import streamlit as st

from src.rag_pipeline import RAGPipeline


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="EduPulse AI | PDF Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #f5f7fc;
        color: #172033;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        color: #172554 !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }

    h2, h3 {
        color: #1e3a8a !important;
        font-weight: 700 !important;
    }

    p, label {
        color: #334155;
    }

    [data-testid="stSidebar"] {
        background: #eef2ff;
        border-right: 1px solid #dbe3f5;
    }

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #1e3a8a !important;
    }

    .hero {
        background: linear-gradient(120deg, #312e81, #4f46e5, #7c3aed);
        padding: 32px;
        border-radius: 20px;
        color: white;
        margin-bottom: 28px;
        box-shadow: 0 8px 24px rgba(79, 70, 229, 0.16);
    }

    .hero h1 {
        color: white !important;
        font-size: 2.4rem !important;
        margin-bottom: 8px;
    }

    .hero p {
        color: #e0e7ff !important;
        font-size: 1.05rem;
        margin-bottom: 0;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.16);
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        margin-bottom: 14px;
    }

    .feature-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        min-height: 130px;
        box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
    }

    .feature-card h3 {
        margin-top: 0;
        font-size: 1.05rem;
        color: #312e81 !important;
    }

    .feature-card p {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 0;
    }

    button[data-baseweb="tab"] {
        font-size: 16px;
        font-weight: 650;
        padding: 14px 22px;
        color: #475569;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4f46e5;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        background: linear-gradient(90deg, #4f46e5, #6366f1);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: linear-gradient(90deg, #4338ca, #4f46e5);
        color: white;
        border: none;
        transform: translateY(-1px);
    }

    .stButton > button:disabled {
        background: #cbd5e1;
        color: #64748b;
    }

    .stTextInput input,
    .stTextArea textarea {
        border-radius: 10px;
        border: 1px solid #cbd5e1;
    }

    [data-testid="stFileUploader"] {
        background: white;
        border: 1px dashed #a5b4fc;
        border-radius: 12px;
        padding: 12px;
    }

    [data-testid="stChatMessage"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }

    [data-testid="stExpander"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }

    [data-testid="stAlert"] {
        border-radius: 10px;
    }

    .stCaption {
        color: #64748b;
    }

    [data-testid="stForm"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 22px;
    }

    .flashcard {
        background: linear-gradient(135deg, #ffffff, #eef2ff);
        border: 1px solid #c7d2fe;
        border-radius: 20px;
        padding: 35px 25px;
        min-height: 180px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(79, 70, 229, 0.08);
    }

    .flashcard-label {
        color: #6366f1;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .flashcard h2 {
        color: #1e1b4b !important;
        font-size: 1.5rem !important;
        margin-top: 18px;
    }

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.85rem;
        padding: 25px 0 5px;
    }

    hr {
        border-color: #e2e8f0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

DEFAULTS = {
    "pipeline": None,
    "document_id": None,
    "document_name": None,
    "chat_history": [],
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


# --------------------------------------------------
# SIDEBAR — PDF UPLOAD
# --------------------------------------------------

with st.sidebar:

    st.markdown("## 📚 EduPulse AI")
    st.caption("Your personal PDF learning assistant")

    st.divider()

    st.markdown("### 📄 Upload your PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF document",
        type=["pdf"],
        accept_multiple_files=False,
        help="Select a PDF document to ask questions about.",
    )

    if uploaded_file is not None:

        st.success(f"Selected: {uploaded_file.name}")
        st.caption(f"File size: {uploaded_file.size:,} bytes")

        if st.button(
            "🚀 Process PDF",
            type="primary",
            use_container_width=True,
        ):

            try:

                with st.spinner("Processing your PDF..."):

                    pdf_bytes = uploaded_file.getvalue()
                    pipeline = RAGPipeline()
                    document_id = pipeline.index_pdf(pdf_bytes)

                    st.session_state["pipeline"] = pipeline
                    st.session_state["document_id"] = document_id
                    st.session_state["document_name"] = uploaded_file.name

                    # Reset previous study data.
                    st.session_state["chat_history"] = []
                    st.session_state["quiz"] = []
                    st.session_state["quiz_answers"] = {}
                    st.session_state["quiz_submitted"] = False
                    st.session_state["flashcards"] = []
                    st.session_state["flashcard_index"] = 0
                    st.session_state["flashcard_revealed"] = False

                    # Remove previous quiz radio selections.
                    for index in range(10):
                        st.session_state.pop(
                            f"quiz_answer_{index}",
                            None,
                        )

                st.success("PDF processed successfully!")
                st.rerun()

            except Exception as exc:
                st.error(f"Unable to process PDF: {exc}")

    if st.session_state["document_id"] is not None:

        st.divider()
        st.markdown("### 🟢 Active Document")
        st.write(st.session_state["document_name"])
        st.caption("Document ID")
        st.code(st.session_state["document_id"])

    st.divider()
    st.caption("Powered by RAG + OpenAI")


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <span class="hero-tag">✨ AI-POWERED LEARNING</span>
        <h1>EduPulse AI</h1>
        <p>
            Transform your PDF documents into an interactive learning
            experience. Ask questions, generate quizzes, and revise
            important concepts with AI.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

if st.session_state["document_id"] is None:

    st.info(
        "👈 Upload a PDF from the sidebar and click Process PDF to get started."
    )

    st.markdown("## What can you do with EduPulse AI?")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.markdown(
            """
            <div class="feature-card">
                <h3>💬 PDF Chat</h3>
                <p>Ask questions and get answers grounded in your PDF.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            """
            <div class="feature-card">
                <h3>📝 Smart Quiz</h3>
                <p>Generate multiple-choice questions and check your score.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:

        st.markdown(
            """
            <div class="feature-card">
                <h3>🗂️ Flashcards</h3>
                <p>Revise important topics using interactive study cards.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --------------------------------------------------
# ACTIVE DOCUMENT DASHBOARD
# --------------------------------------------------

else:

    st.markdown(
        f"### 📄 Studying: {escape(str(st.session_state['document_name']))}"
    )

    st.caption(
        "Your document is processed. Choose a learning tool below."
    )

    chat_tab, quiz_tab, flashcards_tab = st.tabs(
        ["💬 Chat", "📝 Quiz", "🗂️ Flashcards"]
    )


    # --------------------------------------------------
    # CHAT TAB
    # --------------------------------------------------

    with chat_tab:

        st.subheader("💬 Chat with your PDF")

        st.caption(
            "Ask questions about your uploaded document. "
            "Your conversation stays visible while you study."
        )

        if st.button(
            "🗑️ Clear Chat",
            key="clear_chat",
        ):

            st.session_state["chat_history"] = []
            st.rerun()

        # Display previous conversation.
        for message in st.session_state["chat_history"]:

            with st.chat_message(message["role"]):

                if message["is_error"]:
                    st.error(message["content"])
                else:
                    st.write(message["content"])

                if (
                    message["role"] == "assistant"
                    and message["sources"]
                ):

                    with st.expander("📖 View PDF Sources"):

                        for source in message["sources"]:

                            st.markdown(
                                f"**📄 Page {source['page_number']}**"
                            )

                            st.write(source["text"])
                            st.divider()

        question = st.chat_input(
            "Ask a question about your PDF..."
        )

        if question:

            st.session_state["chat_history"].append({
                "role": "user",
                "content": question,
                "sources": [],
                "is_error": False,
            })

            try:

                with st.spinner("Finding an answer..."):

                    result = st.session_state["pipeline"].answer_question(
                        question=question,
                        document_id=st.session_state["document_id"],
                    )

                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": result["answer"],
                    "sources": result["sources"],
                    "is_error": False,
                })

            except Exception as exc:

                st.session_state["chat_history"].append({
                    "role": "assistant",
                    "content": f"Unable to answer question: {exc}",
                    "sources": [],
                    "is_error": True,
                })

            st.rerun()


    # --------------------------------------------------
    # QUIZ TAB
    # --------------------------------------------------

    with quiz_tab:

        st.subheader("📝 Test your knowledge")

        st.caption(
            "Generate multiple-choice questions from your active PDF."
        )

        if st.button(
            "✨ Generate Quiz",
            key="generate_quiz",
            type="primary",
        ):

            try:

                with st.spinner("Creating quiz from your PDF..."):

                    result = st.session_state["pipeline"].generate_quiz(
                        document_id=st.session_state["document_id"],
                        num_questions=5,
                    )

                questions = result.get("questions", [])

                # Store the newly generated questions.
                st.session_state["quiz"] = questions
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False

                # Clear selections from the previous quiz.
                for index in range(10):
                    st.session_state.pop(
                        f"quiz_answer_{index}",
                        None,
                    )

                if result.get("message"):

                    st.info(result["message"])

                elif not questions:

                    st.warning(
                        "No quiz questions were generated. "
                        "Please try again."
                    )

                # No additional st.rerun() is needed here.
                # The quiz is rendered below in this same run.

            except Exception as exc:

                st.error(f"Unable to generate quiz: {exc}")

        quiz = st.session_state["quiz"]

        if quiz:

            st.divider()

            with st.form("quiz_form"):

                for index, item in enumerate(quiz):

                    st.markdown(
                        f"**Question {index + 1}. {item['question']}**"
                    )

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

                    st.caption(
                        f"📄 Source: Page {item['page_number']}"
                    )

                    st.divider()

                submitted = st.form_submit_button(
                    "✅ Check My Answers",
                    use_container_width=True,
                )

            if submitted:
                st.session_state["quiz_submitted"] = True

            if st.session_state["quiz_submitted"]:

                answers = st.session_state["quiz_answers"]

                score = sum(
                    answers.get(index) == item["correct_answer"]
                    for index, item in enumerate(quiz)
                )

                percentage = round((score / len(quiz)) * 100)

                st.divider()
                st.subheader("📊 Quiz Results")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Your Score",
                        f"{score} / {len(quiz)}",
                    )

                with col2:

                    st.metric(
                        "Accuracy",
                        f"{percentage}%",
                    )

                st.progress(percentage / 100)

                if percentage == 100:

                    st.success(
                        "🎉 Excellent! All answers are correct!"
                    )

                elif percentage >= 60:

                    st.success(
                        "👏 Good work! Keep learning."
                    )

                else:

                    st.info(
                        "📚 Keep practicing. You can improve!"
                    )

                st.divider()
                st.markdown("### Answer Review")

                for index, item in enumerate(quiz):

                    selected = answers.get(index)
                    correct = item["correct_answer"]

                    st.markdown(
                        f"**Question {index + 1}. {item['question']}**"
                    )

                    if selected == correct:

                        st.success("Correct answer!")

                    else:

                        st.error(
                            f"Correct answer: {correct}. "
                            f"{item['options'][correct]}"
                        )

                    st.write(item["explanation"])

                    st.caption(
                        f"📄 Source: Page {item['page_number']}"
                    )

                    st.divider()


    # --------------------------------------------------
    # FLASHCARDS TAB
    # --------------------------------------------------

    with flashcards_tab:

        st.subheader("🗂️ Smart Flashcards")

        st.caption(
            "Review key information from your PDF and test your memory."
        )

        if st.button(
            "✨ Generate Flashcards",
            key="generate_flashcards",
            type="primary",
        ):

            try:

                with st.spinner("Creating flashcards from your PDF..."):

                    result = st.session_state["pipeline"].generate_flashcards(
                        document_id=st.session_state["document_id"],
                        num_cards=5,
                    )

                cards = result.get("flashcards", [])

                st.session_state["flashcards"] = cards
                st.session_state["flashcard_index"] = 0
                st.session_state["flashcard_revealed"] = False

                if result.get("message"):

                    st.info(result["message"])

                elif not cards:

                    st.warning(
                        "No flashcards were generated. Please try again."
                    )

                # The new cards are displayed below without an extra rerun.

            except Exception as exc:

                st.error(f"Unable to generate flashcards: {exc}")

        cards = st.session_state["flashcards"]

        if cards:

            st.divider()

            # Keep the index within the valid range.
            index = st.session_state["flashcard_index"]
            index = max(0, min(index, len(cards) - 1))
            st.session_state["flashcard_index"] = index

            card = cards[index]

            st.caption(
                f"CARD {index + 1} OF {len(cards)}"
            )

            st.progress((index + 1) / len(cards))

            front = escape(str(card["front"]))

            st.markdown(
                f"""
                <div class="flashcard">
                    <div class="flashcard-label">Question</div>
                    <h2>{front}</h2>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.write("")

            if st.session_state["flashcard_revealed"]:

                back = escape(str(card["back"]))

                st.markdown(
                    f"""
                    <div class="flashcard">
                        <div class="flashcard-label">Answer</div>
                        <h2>{back}</h2>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.caption(
                    f"📄 Source: Page {card['page_number']}"
                )

            else:

                st.info(
                    "💡 Try answering the question before revealing the answer."
                )

            if st.button(
                "🙈 Hide Answer"
                if st.session_state["flashcard_revealed"]
                else "👁️ Reveal Answer",
                key="toggle_flashcard",
                use_container_width=True,
            ):

                st.session_state["flashcard_revealed"] = (
                    not st.session_state["flashcard_revealed"]
                )

                st.rerun()

            st.write("")

            previous_col, next_col = st.columns(2)

            with previous_col:

                if st.button(
                    "← Previous",
                    disabled=index == 0,
                    key="previous_flashcard",
                    use_container_width=True,
                ):

                    st.session_state["flashcard_index"] -= 1
                    st.session_state["flashcard_revealed"] = False

                    st.rerun()

            with next_col:

                if st.button(
                    "Next →",
                    disabled=index >= len(cards) - 1,
                    key="next_flashcard",
                    use_container_width=True,
                ):

                    st.session_state["flashcard_index"] += 1
                    st.session_state["flashcard_revealed"] = False

                    st.rerun()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        Built with Streamlit, Retrieval-Augmented Generation and OpenAI
        <br>
        EduPulse AI — Learn smarter from your documents.
    </div>
    """,
    unsafe_allow_html=True,
)
