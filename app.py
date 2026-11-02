"""EduPulse AI — PDF question-answering interface."""

import streamlit as st

from src.rag_pipeline import RAGPipeline


st.set_page_config(
    page_title="EduPulse AI",
    page_icon="📚",
    layout="centered",
)

st.title("📚 EduPulse AI")
st.caption("Ask questions about your PDF documents.")

with st.sidebar:
    st.header("Upload your PDF")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
    )

    if uploaded_file:
        st.success(f"Uploaded: {uploaded_file.name}")

if uploaded_file:
    if st.button("Process PDF"):
        try:
            with st.spinner("Processing your PDF..."):
                pipeline = RAGPipeline()

                document_id = pipeline.index_pdf(
                    uploaded_file.getvalue()
                )

                st.session_state["pipeline"] = pipeline
                st.session_state["document_id"] = document_id
                st.session_state["document_name"] = uploaded_file.name

            st.success("PDF processed successfully!")

        except Exception as exc:
            st.error(f"Unable to process PDF: {exc}")

if "document_id" in st.session_state:
    st.subheader(
        f"Ask questions about {st.session_state['document_name']}"
    )

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
else:
    st.info("Upload a PDF and click Process PDF to get started.")
