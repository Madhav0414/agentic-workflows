# multimodal-rag

RAG chat application that answers questions over **text, images, and video in a single vector space**, with source attribution and relevance scores in the UI.

## Pipeline

1. **Ingest** (`ingest_all.py` or individual `ingest_*.py`) — text files are chunked; images get Gemini-vision auto-descriptions; videos are frame-sampled (up to 32 frames) and described. Everything is embedded with Gemini `embedding-2` (768-dim) and upserted to a Pinecone index (`multimodal-rag`) with content-type metadata.
2. **Retrieve** (`app.py`) — each chat message is embedded and the top-5 nearest items are pulled from Pinecone.
3. **Generate** — the chat model answers strictly from retrieved context (the system prompt forbids general-knowledge fallback). Sources are shown as colored badges (text / image / video) with relevance percentages.

## Run it

```bash
pip install -r requirements.txt
cp .env.example .env       # fill in your keys
python setup_index.py      # one-time Pinecone index creation
# put your media in data/ (txt, png/webp/jpg, mp4)
python ingest_all.py
python app.py              # → http://localhost:5000
```

Full walkthrough with troubleshooting: [SETUP.md](SETUP.md).

## Files

| File | Role |
|------|------|
| `app.py` | Flask backend — RAG retrieval + chat endpoint |
| `config.py` | Env config and API clients |
| `embeddings.py` | Gemini embedding functions (text/image/video) |
| `pinecone_db.py` | Vector DB wrapper |
| `ingest_*.py` | Per-modality ingestion tools |
| `query.py` | CLI retrieval tester |
| `templates/`, `static/` | Chat UI |
