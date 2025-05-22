# Kb-Slackbot
A Slack-integrated assistant that enables natural language querying of internal documentation such as runbooks, ADRs, and wikis. It uses OpenAI embeddings with a Chroma vector store for semantic search and returns summarized, context-aware answers directly in Slack. Falls back to GPT-based general knowledge when no relevant information found.

# Slack Knowledge Assistant Bot

A Slack-integrated assistant that enables natural language querying of internal documentation (e.g., runbooks, ADRs, wikis). It performs semantic search over a vector store backed by ChromaDB and returns summarized, contextual answers using OpenAI’s language models.

If internal documentation is insufficient, it falls back to GPT-powered general knowledge to ensure helpful responses in all cases.

---

## Features

- 🔍 **Semantic Search**: Uses OpenAI embeddings to semantically match questions to internal documentation.
- 🧠 **Contextual Summarization**: Returns only the most relevant excerpts, not full wiki pages.
- 💬 **Slack Integration**: Ask questions directly in Slack via mentions.
- 📄 **Source Linking**: Provides links to the original documentation sources.
- 🧩 **Fallback to GPT**: Uses GPT for DevOps/infra questions when no internal match is found.
- 🚫 **Reduces Tribal Knowledge Dependency**: Engineers don’t need to know specific document titles or locations.

---

## Example Use Cases

- “How do I block an IP in AWS WAF?”
- “Why is the Go audit indexer lagging?”
- “How do I manually reindex the catalog?”

---

## Architecture Overview

```plaintext
Slack → Slack Bolt App (Python) → 
↓
Extract Question → Embed via OpenAI → Query Chroma Vector Store → 
↓                                         ↓
Match Found?                           No Match
↓                                          ↓
Summarize + Cite Source        →      Use GPT to Answer
↓
Respond in Slack Thread

---

## Setup Instructions

### Clone the repository
git clone https://github.com/reshmachitre/Kb-Slackbot.git
cd slack-knowledge-assistant

### Create and Activate a Virtual Environment
python3 -m venv venv
source venv/bin/activate



