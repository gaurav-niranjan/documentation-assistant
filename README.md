# Documentation Assistant

A small retrieval-augmented generation (RAG) project for asking questions over documentation. The pipeline uses Pinecone for vector storage and retrieval, and Gemini via the OpenAI-compatible API for answer generation. Both services can be used with free-tier accounts.

## What the project does

The repository is organized around a simple end-to-end workflow:

1. Convert a source PDF into Markdown.
2. Normalize the Markdown structure so section headings can be chunked cleanly.
3. Split the documentation into section-sized chunks.
4. Store the chunks in a Pinecone index.
5. Retrieve the most relevant chunks for a user question.
6. Send the retrieved context to Gemini to generate the final answer.

## Source Layout

- [src/chat_app/pdf_parser/docling_parser.py](src/chat_app/pdf_parser/docling_parser.py) converts the source PDF into Markdown and writes the result to `data_sources/lavafox.md`.
- [src/chat_app/pdf_parser/h2_to_h1.py](src/chat_app/pdf_parser/h2_to_h1.py) promotes numbered `##` headings to `#` headings so the document is easier to split into chunks.
- [src/chat_app/pinecone_utils/create_index.py](src/chat_app/pinecone_utils/create_index.py) creates the Pinecone index used by the project.
- [src/chat_app/pinecone_utils/save_vectors.py](src/chat_app/pinecone_utils/save_vectors.py) reads the Markdown documentation, splits it into chunks, and uploads the records to Pinecone.
- [src/chat_app/doc_assistant/RAG_chatbot.py](src/chat_app/doc_assistant/RAG_chatbot.py) runs the RAG chat loop: it searches Pinecone, builds context from the retrieved chunks, and asks Gemini to answer.
- [src/chat_app/doc_assistant/chatbot.py](src/chat_app/doc_assistant/chatbot.py) is a simpler baseline chatbot that answers directly from the full documentation text without retrieval.

## Data Flow

The project currently uses the `lavafox` documentation under `data_sources/` as example content. The main RAG path is:

`data_sources/firefox.pdf` -> Markdown -> `data_sources/lavafox.md` -> chunked records -> Pinecone namespace `lavafox` -> Gemini answer generation.

The Pinecone index name used in the code is `gross-app`.

## Requirements

The project depends on Python 3.10+ and these packages:

- `docling`
- `google-genai`
- `openai`
- `pinecone`
- `python-dotenv`

## Environment Variables

Set these values before running the scripts:

- `GEMINI_API_KEY`
- `PINECONE_API_KEY`

## Typical Workflow

1. Convert the source document to Markdown.
2. Optionally run the heading-normalization step.
3. Create the Pinecone index if it does not exist.
4. Upload the documentation chunks into Pinecone.
5. Run the RAG chatbot and ask a question.

## Notes

- The Gemini calls use the OpenAI-compatible Gemini endpoint, which lets the project use the `openai` client library with Gemini models.
- The RAG chatbot retrieves the top 3 matching chunks from Pinecone before prompting the model.
- The example code is built around the `lavafox` manual, but the same structure can be adapted to other documentation sets.
