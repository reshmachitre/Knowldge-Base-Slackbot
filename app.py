import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from openai import OpenAI
import chromadb
from chromadb.config import Settings

# Map source filenames to wiki URLs
SOURCE_LINKS = {
    "incident_deploy.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259327557813/Incident+Deploys",
    "salsify_paas_primer.txt":"https://salsify.atlassian.net/wiki/spaces/ENG/pages/673185905/Salsify+s+PaaS+Primer+Product+XM",
    "elasticsearch_master_node_crash.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259340369974/Elasticsearch+Master+Node+Crash+Runbook",
    "manual_reindexing.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259863412784/Manual+Reindexing",
    "delayed_jobs.txt": "https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259373531351/Delayed+Jobs",
    "analysis_db_out_of_space.txt": "https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/260279599105/Analysis+DB+running+out+of+free+disk+space",
    "web_request_flooding.txt": "https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/260141973512/Handling+Web+Request+Flooding+by+a+Specific+User+or+Organization",
    "workflow_chrome_extension.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259658219629/Updating+our+workflow+Chrome+Extension",
    "audit_lag_runbook.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259877896766/Audit+Lag+Runbook",
    "audit_event_decoding_error.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259877896766/Audit+Event+Decoding+Error",
    "go_audit_indexer.txt":"https://salsify.atlassian.net/wiki/spaces/PIMCORE/pages/259882811405/Go+Audit+Indexer+Design",
    "built_in_workflow_steps.txt":"https://developers.salsify.com/docs/built-in-step-types",
    "high_sku_process_evaluation.txt":"https://salsify.atlassian.net/wiki/spaces/PM/pages/2120712201/High+SKU+Process+Large+Opportunity+Evaluation",
    "target_schema_definition_language.txt":"https://salsify.atlassian.net/wiki/spaces/ENG/pages/42237956/Target+Schema+Definition+Language",
    "task_indexing_sync.txt":"https://salsify.atlassian.net/wiki/spaces/HD/pages/259254059116/Task+Indexing+Failure+Primary+Runbook+Org+Sync"
    # Add more mappings here...
}


# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Slack app
app = App(token=os.getenv("SLACK_BOT_TOKEN"))

# Persistent ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_store")
collection = chroma_client.get_or_create_collection("knowledge_base")

def get_context(question, threshold=0.75, min_relevance_cutoff=0.30):
    res = client.embeddings.create(input=[question], model="text-embedding-ada-002")
    q_embed = res.data[0].embedding

    results = collection.query(
        query_embeddings=[q_embed],
        n_results=8,
        include=["documents", "metadatas", "distances"]
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    filtered = [
        (doc, meta, dist) for doc, meta, dist in zip(documents, metadatas, distances)
        if dist < threshold
    ]

    if not filtered:
        return "No relevant documents found.", [], False

    # Sort by relevance
    filtered.sort(key=lambda x: x[2])

    # Determine if at least one is strong
    has_strong_match = any(dist < 0.50 for _, _, dist in filtered)

    context_chunks = []
    filtered_metas = []

    for doc, meta, dist in filtered:
        filename = meta["source"]
        url = SOURCE_LINKS.get(filename)
        tag = f"<{url}|Source: {filename}>" if url else f"[Source: {filename}]"
        context_chunks.append(f"{tag}\n{doc}")
        filtered_metas.append(meta)

    return "\n\n".join(context_chunks), filtered_metas, has_strong_match, filtered

# 💬 Use GPT to generate an answer based on retrieved context
def ask_gpt(question, context):
    system_msg = (
        "You are a helpful assistant. If the provided context is relevant, use it to answer. "
        "If it's not sufficient, you may rely on your own general knowledge to answer accurately."
    )

    prompt = f"""
Use the context below to answer the question. If the context contains sources (e.g., [Source: filename]), cite the most relevant one in your answer.

Context:
{context}

Question: {question}
"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt.strip()}
        ]
    )

    return response.choices[0].message.content

def ask_gpt_generic(question):
    system_msg = "You are a helpful assistant answering general tech and DevOps questions."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question}
        ]
    )

    return response.choices[0].message.content

@app.event("app_mention")
def handle_mention(event, say):
    user_q = event["text"].replace(f"<@{event['user']}>", "").strip()
    context, metadatas, is_strong_match, filtered = get_context(user_q)


    if not metadatas:
        # Nothing matched at all
        answer = ask_gpt(user_q, "")
        say(f"{answer}\n\n⚠️ No internal documentation matched your question.")
        return

    answer = ask_gpt(user_q, context)

    # Keep only the top 3 most relevant sources
    top_sources = []
    seen_sources = set()
    for _, meta, _ in filtered:
        source = meta["source"]
        if source not in seen_sources:
            seen_sources.add(source)
            top_sources.append(source)
        if len(top_sources) == 3:
            break

   # Generate links
    links = [
        f":link: <{SOURCE_LINKS[source]}|{source}>" if source in SOURCE_LINKS
        else f":page_facing_up: {source}"
        for source in top_sources
    ]
    sources_text = "\n".join(links)

    if is_strong_match:
        say(f"{answer}\n\n:satellite: Related Docs:\n{sources_text}")
    else:
        say(f"{answer}\n\n⚠️ Documentation was a weak match. Answer may rely on general knowledge.\n\n:satellite: Related (but weak) Docs:\n{sources_text}")


# 🚀 Start the Slack app
if __name__ == "__main__":
    handler = SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN"))
    handler.start()
