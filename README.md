# Kb-Slackbot

A Slack-integrated assistant that enables natural language querying of internal documentation such as runbooks, ADRs, and wikis. It uses OpenAI embeddings with a Chroma vector store for semantic search and returns summarized, context-aware answers directly in Slack. Falls back to GPT-based general knowledge when no relevant information is found.

## Features

- 🔍 **Semantic Search**: Uses OpenAI embeddings to semantically match questions to internal documentation
- 🧠 **Contextual Summarization**: Returns only the most relevant excerpts, not full wiki pages
- 💬 **Slack Integration**: Ask questions directly in Slack via mentions
- 📄 **Source Linking**: Provides links to the original documentation sources
- 🧩 **Fallback to GPT**: Uses GPT for DevOps/infra questions when no internal match is found
- 🚫 **Reduces Tribal Knowledge Dependency**: Engineers don't need to know specific document titles or locations

## Example Use Cases

- "How do I block an IP in AWS WAF?"
- "Why is the Go audit indexer lagging?"
- "How do I manually reindex the catalog?"

## Architecture Overview

```
Slack → Slack Bolt App (Python) → 
↓
Extract Question → Embed via OpenAI → Query Chroma Vector Store → 
↓                                         ↓
Match Found?                           No Match
↓                                          ↓
Summarize + Cite Source        →      Use GPT to Answer
↓
Respond in Slack Thread
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/reshmachitre/Kb-Slackbot.git
cd slack-knowledge-assistant
```

### 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the project root:

```env
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
SLACK_APP_TOKEN=xapp-your-slack-app-token
OPENAI_API_KEY=sk-...
```

### 5. Populate Chroma Vector Store

You must embed and store your internal documents (runbooks, ADRs, etc.) in ChromaDB using OpenAI embeddings. This typically happens in a separate ingestion script. 

Ensure your `chroma_store/` contains the indexed vectors.

> **Note**: If needed, we can provide a script to do this.

### 6. Run the Bot

```bash
python app.py
```

The bot will start and listen for mentions via Socket Mode.

## Slack Usage

Mention the bot in a Slack channel or DM:

```
@knowledge-bot How do I reindex the catalog?
```

It will respond with:
- A summary of the best-matching documentation
- Relevant source links
- A fallback GPT response if no internal docs matched

## Document Source Mapping

The bot uses a static map of source files to URLs (e.g., Confluence pages). Update the `SOURCE_LINKS` dictionary in `app.py` as you add more documents.

## Dependencies

- Slack Bolt (Python)
- OpenAI Python SDK
- ChromaDB
- python-dotenv

Install them with:

```bash
pip install -r requirements.txt
```

## Troubleshooting

- **Missing ChromaDB or Documents**: Ensure your vector store is properly populated and path is correct
- **Bot Not Responding**: Check your Slack app permissions, tokens, and that it's running in Socket Mode
- **Filtered Error**: Ensure variable scopes are consistent if modifying the `get_context()` logic

## Future Improvements

- Add streaming responses to Slack
- Allow ingestion via Slack DM/upload
- Admin UI for document ingestion and monitoring
- Add confidence scores in response metadata
