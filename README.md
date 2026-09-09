# Documentation Assistant

A simple multi-product retrieval-augmented generation (RAG) assistant for software documentation. The app uses Pinecone for retrieval and Gemini for answer generation through the OpenAI-compatible API.

## Overview

This repository builds a lightweight support assistant for multiple fictional GROSS products:

- Lavafox (web browser)
- Birdmail (email client)
- OpenMRS (medical record system)
- Paintscape (SVG drawing tool)
- Blogpress (CMS)

The end-to-end pipeline is:

1. Convert a source PDF into Markdown.
2. Normalize heading levels for consistent chunk boundaries.
3. Split each manual into chunks by H1 sections.
4. Upsert chunks to Pinecone under a shared namespace.
5. Retrieve top matching chunks for each user query.
6. Pass retrieved context to Gemini and return the answer.

## Source Layout

- [src/chat_app/pdf_parser/docling_parser.py](src/chat_app/pdf_parser/docling_parser.py): Converts supported PDFs to Markdown for Paintscape, OpenMRS, Birdmail, and Blogpress.
- [src/chat_app/pdf_parser/h2_to_h1.py](src/chat_app/pdf_parser/h2_to_h1.py): Promotes numbered H2 headings to H1 headings for cleaner chunking.
- [src/chat_app/pinecone_utils/create_index.py](src/chat_app/pinecone_utils/create_index.py): Creates Pinecone index gross-app using hosted embedding model llama-text-embed-v2.
- [src/chat_app/pinecone_utils/save_vectors.py](src/chat_app/pinecone_utils/save_vectors.py): Chunks all Markdown manuals and upserts them into namespace all-gross.
- [src/chat_app/doc_assistant/RAG_chatbot.py](src/chat_app/doc_assistant/RAG_chatbot.py): Single-product interactive RAG chat (Lavafox namespace).
- [src/chat_app/evals/chatbot.py](src/chat_app/evals/chatbot.py): Multi-product interactive RAG chat for the all-gross namespace.
- [src/chat_app/doc_assistant/chatbot.py](src/chat_app/doc_assistant/chatbot.py): Baseline non-RAG chatbot that injects one full manual directly in the prompt.

## Data Sources

Documentation files live in data_sources:

- [data_sources/lavafox.md](data_sources/lavafox.md)
- [data_sources/birdmail.md](data_sources/birdmail.md)
- [data_sources/openMRS.md](data_sources/openMRS.md)
- [data_sources/paintscape.md](data_sources/paintscape.md)
- [data_sources/blogpress.md](data_sources/blogpress.md)

The multi-product pipeline writes vectors into:

- Index: gross-app
- Namespace: all-gross

## Setup

Requirements:

- Python 3.10+
- Pinecone account and API key
- Gemini API key

Install dependencies:

```bash
uv sync
```

## Environment Variables

Create a .env file in the repository root:

```env
GEMINI_API_KEY=your_gemini_key
PINECONE_API_KEY=your_pinecone_key
```

## Run Pipeline

1. Convert PDFs to Markdown:

```bash
uv run python src/chat_app/pdf_parser/docling_parser.py
```

2. Normalize Markdown headings:

```bash
uv run python src/chat_app/pdf_parser/h2_to_h1.py
```

3. Create Pinecone index (one-time):

```bash
uv run python src/chat_app/pinecone_utils/create_index.py
```

4. Chunk and upsert vectors:

```bash
uv run python src/chat_app/pinecone_utils/save_vectors.py
```

5. Start multi-product RAG chat:

```bash
uv run python src/chat_app/evals/chatbot.py
```

Type exit to quit the chatbot.

## Alternative Chat Modes

- Single-manual RAG mode:

```bash
uv run python src/chat_app/doc_assistant/RAG_chatbot.py
```

- Baseline non-RAG mode:

```bash
uv run python src/chat_app/doc_assistant/chatbot.py
```

## Notes

- Gemini is used through the OpenAI-compatible endpoint, so calls are made with the openai Python client.
- Retrieval currently uses top_k=3 results from Pinecone.
- The embedding/indexing flow uses Pinecone hosted embeddings with model llama-text-embed-v2.
