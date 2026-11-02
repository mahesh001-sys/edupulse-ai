# EduPulse AI — PDF Question Answering with RAG

An AI-powered study assistant that helps students understand their study materials by asking questions directly from PDF documents.

EduPulse AI uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents and generate context-aware answers with page-level citations.

## Overview

Students often spend considerable time searching through lengthy textbooks, lecture notes, and study materials to find answers to specific questions.

EduPulse AI aims to simplify this process by allowing students to upload their PDF documents and interact with their content through a conversational interface.

Instead of relying only on the language model's general knowledge, the application retrieves relevant information from the uploaded documents and uses it to generate answers.

## Features

- **PDF Question Answering:** Ask questions about the content of uploaded PDF documents.
- **Retrieval-Augmented Generation:** Retrieve relevant document sections before generating an answer.
- **Semantic Search:** Use vector embeddings to identify relevant content based on meaning.
- **Page-Level Citations:** Display source page references to help users verify answers.
- **Interactive Chat Interface:** Interact with study materials through a Streamlit-based interface.
- **Document-Based Responses:** Ground answers in retrieved document content to reduce unsupported responses.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application development |
| Streamlit | Interactive web interface |
| ChromaDB | Vector storage and similarity search |
| RAG | Document retrieval and answer generation |
| Embedding Models | Convert document text into vectors |
| LLM | Generate context-aware answers |
| PyPDF | PDF text extraction |

*The final embedding model and LLM provider will depend on the application's implementation.*

## How It Works

EduPulse AI follows a two-stage RAG pipeline.

### 1. Document Ingestion

1. The user uploads a PDF document.
2. The application extracts text from the PDF.
3. The extracted text is divided into smaller chunks.
4. Each chunk is converted into a vector embedding.
5. The embeddings and associated metadata, including page numbers, are stored in ChromaDB.

### 2. Question Answering

1. The user submits a question through the Streamlit chat interface.
2. The question is converted into an embedding.
3. ChromaDB retrieves the most relevant document chunks.
4. The retrieved context is provided to the language model.
5. The model generates an answer based on the retrieved content.
6. The application displays the answer along with its source page references.

```text
                PDF Document
                      |
                      v
                Extract Text
                      |
                      v
               Split into Chunks
                      |
                      v
               Generate Embeddings
                      |
                      v
              Store in ChromaDB
                      |
                      v
User Question --> Semantic Search
                      |
                      v
             Retrieve Relevant Chunks
                      |
                      v
              LLM Generates Answer
                      |
                      v
           Answer + Page Citations
```

## Project Structure

```text
edupulse-ai/
│
├── src/                # Application source code
├── tests/              # Test cases
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # Project documentation
```

## Getting Started

### Prerequisites

- Python 3.10 or later
- Git
- pip
- A compatible LLM provider and API key, if required by the selected model

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/mahesh001-sys/edupulse-ai.git
cd edupulse-ai
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

Activate the environment:

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

If the selected LLM provider requires an API key, create a `.env` file in the project root and add the required configuration.

```env
LLM_API_KEY=your_api_key_here
```

Use the environment variable name expected by the application. Never commit API keys or other credentials to GitHub.

**5. Run the application**

Once the Streamlit entry-point file is configured, start the application using:

```bash
streamlit run src/app.py
```

Open the local URL displayed in your terminal to access the application.

## Testing

The repository includes a `tests/` directory for validating application behavior.

Run the tests using:

```bash
python -m pytest
```

## Project Goals

- Build a working PDF-based question-answering application.
- Understand and implement the complete RAG pipeline.
- Improve answer relevance through semantic retrieval.
- Provide traceable answers using source-page citations.
- Develop practical experience with Python, vector databases, and generative AI.

## Future Improvements

- Support multiple PDF documents in a single knowledge base.
- Improve retrieval quality using better embedding models and reranking.
- Add conversation history and document management.
- Support scanned PDFs using OCR.
- Improve error handling and document-processing feedback.
- Deploy the application for public access.

## Learning Outcomes

Through this project, I am developing practical knowledge of:

- Retrieval-Augmented Generation (RAG)
- PDF text extraction and document processing
- Text chunking and embedding generation
- Vector databases and semantic similarity search
- LLM-based question answering
- Building interactive AI applications with Streamlit
- Testing and maintaining Python applications

## Author

**Banoth Mahesh Kumar**

B.Tech Information Technology | 2026 Graduate

[GitHub Profile](https://github.com/mahesh001-sys)

[EduPulse AI Repository](https://github.com/mahesh001-sys/edupulse-ai)

---

*EduPulse AI is an educational project developed to explore Retrieval-Augmented Generation and document-based AI question answering.*
