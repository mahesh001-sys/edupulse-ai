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

# Keep the pipeline and selected document available across Streamlit reruns.
if "pipeline" not in st.session_state:
    st.session_state["pipeline"] = None

if "document_id" not in st.session_state:
    st.session_state["document_id"] = None

if "document_name" not in st.session_state:
    st.session_state["document_name"] = None


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

                st.success("PDF processed successfully!")

            except Exception as exc:
                st.error(f"Unable to process PDF: {exc}")


if st.session_state["document_id"] is not None:
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
