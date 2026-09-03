# Documentation Assistant

This project is a small documentation-focused assistant built to help users ask questions about product documentation and retrieve answers from source material.

## Project structure

The work in this repository is centered under the src directory:

- src/chat_app/doc_assistant/chatbot.py: a conversational assistant that loads product documentation, creates a support-style chat context, and answers user questions using the OpenAI-compatible Gemini API.
- src/chat_app/pdf_parser/docling_parser.py: a parser utility that converts PDF documents into Markdown so they can be used as source material for the assistant.

This project is intended for building and experimenting with documentation retrieval and AI-powered Q&A workflows.
