# Onboarding Agent

A full-stack onboarding assistant for customer registration and automated email-based conversations, powered by FastAPI, Streamlit, Supabase, OpenAI, and a Retrieval-Augmented Generation (RAG) pipeline.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [RAG Pipeline](#rag-pipeline)
- [Project Structure](#project-structure)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

- Customer onboarding via a web form (Streamlit frontend)
- Backend API for registration and email processing (FastAPI)
- Automated welcome emails and ongoing email conversations
- Conversation logging to Supabase
- Retrieval-Augmented Generation (RAG) for context-aware LLM responses using a vector store (ChromaDB)
- Modular codebase for easy extension

---

## Architecture

- **Frontend:** Streamlit app for customer registration
- **Backend:** FastAPI server for API endpoints and business logic
- **Email Automation:** Reads and replies to emails using IMAP/SMTP
- **Conversation Logging:** Stores all interactions in Supabase (`conversation_log` table)
- **RAG Pipeline:** Uses ChromaDB to retrieve relevant FAQ chunks and OpenAI for LLM responses

---

## Setup

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd Onboarding\ agent
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your credentials, or edit `.env` directly:

```env
SUPABASE_URL=...
SUPABASE_KEY=...
BaseURL="http://localhost:8000"
SUBMISSION_END_POINT="/register_customer"
SENDGRID_API_KEY=...
FROM_EMAIL=...
EMAIL_ACCOUNT=...
EMAIL_PASSWORD=...
IMAP_SERVER=imap.gmail.com
OPENAI_API_KEY=...
```

---

## Running the Application

### 1. Start the FastAPI Backend

```sh
uvicorn backend.main:app --reload
```

### 2. Start the Streamlit Frontend

```sh
streamlit run frontend/app.py
```

### 3. Start the Email Reader Loop

This script checks for new emails every 30 seconds and processes them:

```sh
python backend/run_reader_loop.py
```

### 4. (Optional) Ingest FAQ Documents into the Vector Store

To add/update FAQ documents for RAG:

```sh
python3 -c "from backend.vectorstore.update_faq import update_faq_for_bank; update_faq_for_bank('backend/vectorstore/faqdocs/SBI_Savings_Account_FAQ.pdf')"
```

---

## RAG Pipeline

- **FAQ Ingestion:** `backend/vectorstore/faq_ingestor.py` splits PDF FAQ documents, embeds them, and stores them in ChromaDB.
- **Retrieval:** `backend/vectorstore/rag_retriever.py` retrieves top-k relevant chunks for a user query.
- **LLM Generation:** `backend/generator.py` combines retrieved context and conversation history, then calls OpenAI's API for a response.

---

## Project Structure

```
.env
requirements.txt
backend/
    __init__.py
    conversation.py
    crud.py
    email_reader.py
    email_utils.py
    generator.py
    inspection.py
    logger.py
    main.py
    models.py
    run_reader_loop.py
    runner.py
    logs/
    vector_store/
    vectorstore/
frontend/
    app.py
```

---

## Troubleshooting

- **ModuleNotFoundError:** Ensure you run scripts from the project root and that `backend/` has an `__init__.py`.
- **Email Issues:** Double-check your email credentials and IMAP/SMTP settings in `.env`.
- **Vector Store Issues:** Use `backend/inspection.py` to inspect your ChromaDB collections and FAQ chunks.
- **Supabase Issues:** Ensure your Supabase URL and key are correct and the `conversation_log` table exists.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
