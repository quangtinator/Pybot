# App Design & Interview Discussion Notes

This document outlines the core architectural decisions, assumptions, and specific implementations for the AI Travel Assistant. It is intended to serve as a guide for the technical interview discussion.

---

## 1. How you handled different document formats

**Implementation:** We created a localized `DocumentTool` that acts as a secure file-system scanner.

- **Text & Markdown (.txt, .md):** Handled natively using Python's `open()` function with `utf-8` encoding. The text is read directly into memory.
- **PDFs (.pdf):** Handled via the lightweight `pypdf` library. The bot iterates through pages, extracting pure text content.
- **Unification:** All extracted text is concatenated into a single, clearly segmented string (e.g., `--- filename.md --- \n [Content]`). This unified string is then returned to the LLM. Because modern context windows (like Gemini's) are massive, dumping a small collection of text documents directly into the prompt is faster, cheaper, and more accurate than chunking.

## 2. How the chatbot decides when to fetch external data

**Implementation:** We rely on an **Agentic Tool Calling** architecture via Google's Gemini SDK.

- We mapped our deterministic Python functions to the LLM using the Strategy Pattern (`BaseTool`).
- Instead of writing giant `if/else` regex statements to guess the user's intent, we provided the LLM with exact JSON schemas of our tools generated automatically from our Python **docstrings**.
- **System Heuristics:** We injected explicit behavioral triggers in the docstrings. For example, the `DocumentTool` docstring tells the LLM: _"ALWAYS trigger this tool immediately if the user's prompt contains the word 'my'."_ The LLM acts as the routing brain, intelligently classifying intents and calling the appropriate function when its confidence threshold is met.

## 3. How the integration with external services works

**Implementation:** External integrations are completely decoupled from the AI logic.

- We utilize Python's `requests` library to interact with external REST APIs (e.g., _WeatherAPI_ for real-time weather, _Frankfurter API_ for live currency conversion).
- Each tool runs within isolated `try/except` blocks. If an external API goes down or times out, the tool gracefully returns a localized text error (e.g., _"Failed to fetch live currency rates"_) back to the LLM. The LLM then apologizes to the user naturally, preventing the actual server from crashing.

---

## Technical Deep Dives & Architectural Decisions

### Why didn't we use proper RAG (Retrieval-Augmented Generation)?

For a **"small collection of documents"**, full RAG (using Vector databases like Chroma/Pinecone, generating embeddings, and chunking documents) introduces unnecessary architectural complexity and latency.

- **Simplicity:** The prompt explicitly asked to "keep the solution simple".
- **Context Windows:** Modern LLMs easily handle 100k - 2M tokens. Directly injecting a few PDFs and Markdown tables into the context window guarantees 100% retrieval accuracy without risking the loss of context that happens with poor vector chunking. RAG solves a _scale_ problem. We don't have a scale problem yet.

### Is API validation needed or not?

**Yes, absolutely.** We used **Pydantic** in our FastAPI routes for this.

- **Cost & Security:** If a malicious script hits our API with an infinitely long string, Google Gemini will charge us for those tokens, or the server will run out of memory. Pydantic's `max_length=1000` violently drops bad requests before they ever reach the AI.
- **Defensive Engineering:** Returning an automatic HTTP `422 Unprocessable Entity` is standard REST methodology. It prevents our server from throwing deadly `500 Internal Server Errors` because a required JSON key was missing.

### Why set the LLM Temperature at `0.7` instead of `0.3` for Tool Calling?

In a strictly deterministic system (e.g., code generation or pure data extraction), `0.1 - 0.3` is preferred to prevent hallucinations.
However, this is a **Travel Assistant**. We want it to be conversational, engaging, and slightly creative in how it formats the data it retrieves.
By setting it to `0.7`, we allow the bot's _personality_ to shine, while the strict Pydantic rules and Python Tool layers guarantee that the _backend data execution_ is strictly locked down. The LLM is creative with the _words_, but the Python code guarantees the _facts_.

---

## What you would change or improve with more time

1. **True RAG Implementation:** If the user’s personal data grew from 5 files to 5,000 files/manuals, I would replace the `DocumentTool` with a Vector Database solution (like LangChain + Pinecone) to perform semantic search, as sending 5,000 files in one prompt would cause latency and cost issues.
2. **Persistent State/Database:** The current session is held in FastAPI's memory state and the mock booking is a static dictionary. I would connect a PostgreSQL or MongoDB database to store booking states and user chat histories permanently.
3. **Authentication:** I would add JWT (JSON Web Tokens) or OAuth2 to securely map specific users to specific document folders, rather than a global `/data` folder.
4. **Streaming Responses:** Implementing Server-Sent Events (SSE) so the UI types out the response word-by-word, drastically reducing the perceived waiting latency for the user.
5. **Observability:** Replace Python `print()` statements with standard `logging` to track API request times, tool failure rates, and token usage for monitoring via Datadog or Grafana.
