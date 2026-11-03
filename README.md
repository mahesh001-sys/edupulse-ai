
# EduPulse AI — PDF Study Assistant with RAG

EduPulse AI is an AI-powered study assistant that helps students learn from PDF documents. It uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant passages and generate document-grounded answers, quizzes, and flashcards with page references.

## Features

- **PDF question answering:** Ask questions about uploaded study materials.
- **Semantic retrieval:** Find relevant document passages using vector embeddings.
- **Page references:** Show source pages so users can verify information.
- **Interactive chat:** Explore PDF content through a Streamlit interface.
- **Quiz generation:** Create multiple-choice questions from retrieved PDF content.
- **Flashcard generation:** Create question-and-answer cards from retrieved PDF content.
- **Document-grounded study materials:** Keep generated answers, quizzes, and flashcards based on retrieved text.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| ChromaDB | Vector storage and similarity search |
| Embedding model | Convert text into vectors for retrieval |
| OpenAI API | Generate answers and study materials |
| PyPDF | Extract text from PDFs |

## How It Works

### 1. Document ingestion

1. The user uploads a PDF.
2. The application extracts text and divides it into chunks.
3. Each chunk is converted into an embedding.
4. The embeddings and metadata, including page numbers, are stored in ChromaDB.

### 2. Retrieval and study material generation

1. The user asks a question or requests a quiz or flashcards.
2. The application retrieves relevant chunks from ChromaDB.
3. The retrieved text is passed to the language model.
4. The application presents the generated response with page references where available.

## Project Structure

```text
edupulse-ai/
├── app.py
├── src/
│   ├── api/
│   ├── chunking/
│   ├── embeddings/
│   ├── ingestion/
│   ├── llm/
│   ├── prompts/
│   ├── retrieval/
│   ├── utils/
│   └── vectordb/
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- pip
- An OpenAI API key for model-generated answers, quizzes, and flashcards

### 1. Clone the repository

```bash
git clone https://github.com/mahesh001-sys/edupulse-ai.git
cd edupulse-ai
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Configure the OpenAI API key using the environment-variable name expected by the application. Keep credentials in a local `.env` file or your environment, and never commit them to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL shown in the terminal.

## Testing

Run the test suite from the project root:

```bash
python -m pytest -q
```

The project’s latest reported test run completed with **32 passed**.

## Project Goals

- Build a PDF-based question-answering and study assistant.
- Implement a complete RAG pipeline.
- Improve retrieval relevance through semantic search.
- Provide traceable responses using source-page references.
- Practice building and testing an AI application with Python, vector databases, and Streamlit.

## Future Improvements

- Support multiple PDFs in one knowledge base.
- Improve retrieval with reranking and retrieval-quality evaluation.
- Add conversation history and document management.
- Support scanned PDFs using OCR.
- Improve processing feedback and error handling.
- Deploy the application for public access.

## Author

**Banoth Mahesh Kumar**  
B.Tech Information Technology | 2026 Graduate

- [GitHub Profile](https://github.com/mahesh001-sys)
- [EduPulse AI Repository](https://github.com/mahesh001-sys/edupulse-ai)

---

*EduPulse AI is an educational project exploring Retrieval-Augmented Generation and document-based AI study tools.*
