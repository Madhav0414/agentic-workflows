# Multimodal RAG Chat Setup Guide

## 📋 What's Been Built

- **Backend**: Flask app with Claude Sonnet RAG pipeline
- **Frontend**: Modern chat UI with real-time streaming
- **Ingestion**: All media (text, images, video) auto-processed
- **Vector DB**: Pinecone with Gemini Embedding 2
- **Chat**: Claude Sonnet with retrieved context

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Fill in API Keys in `.env`
```
GEMINI_API_KEY=your-gemini-api-key
PINECONE_API_KEY=your-pinecone-api-key
OPENROUTER_API_KEY=your-openrouter-api-key   # optional fallback
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Step 3: Create Pinecone Index (One-time)
```bash
python setup_index.py
```
Output: `Index 'multimodal-rag' created successfully.`

### Step 4: Ingest Your Media
```bash
python ingest_all.py
```
This will automatically:
- Read all `.txt` files from `data/` and chunk them
- Embed all images (`.webp`, `.png`, `.jpg`, etc.)
- Embed the video (up to 32 frames sampled)
- Upload everything to Pinecone

Expected output:
```
Found 2 text files, 4 images, 1 video
✅ Total items ingested: 7
```

### Step 5: Start the Web App
```bash
python app.py
```

Then open your browser to: **http://localhost:5000**

## 💬 What You Can Ask

- Ask about the text content: "What does text1.txt say?"
- Ask about images: "What's in the MICROSOFT-OPENAI image?"
- Ask about the video: "Describe the video"
- Cross-modal: "Tell me everything about my content"
- Summarization: "Summarize what I have"

## 📁 Project Structure

```
embedding_demo/
├── app.py                      # Flask backend with RAG
├── config.py                   # Config & API clients
├── embeddings.py               # Gemini embedding functions
├── pinecone_db.py              # Vector DB wrapper
├── setup_index.py              # Create Pinecone index
├── ingest_*.py                 # Individual ingestion tools
├── ingest_all.py               # Auto-ingest everything
├── query.py                    # CLI query tool
├── requirements.txt            # Python dependencies
├── .env                        # API keys
├── data/                       # Your media files
├── templates/index.html        # Chat UI
└── static/
    ├── style.css               # Styling
    └── script.js               # Frontend logic
```

## 🔧 Troubleshooting

**"ANTHROPIC_API_KEY not set"**
- Add your Anthropic API key to `.env`

**"Index not found"**
- Run `python setup_index.py` first

**"No results found" in chat**
- Make sure you ran `python ingest_all.py`
- Check Pinecone dashboard to verify vectors are uploaded

**Port 5000 already in use**
- Edit `app.py` line 67: change `port=5000` to another port like `5001`

## 📊 What Happens When You Chat

1. Your message is embedded using Gemini Embedding 2
2. Top 5 similar items retrieved from Pinecone (text chunks, images, video)
3. Context built from retrieved items
4. Claude Sonnet generates answer with full context
5. Sources displayed with relevance scores

## 🎯 Advanced Usage

**Run individual ingestion:**
```bash
# Single text file
python ingest_text.py --file data/document.txt --id my-doc

# Single image
python ingest_images.py --path data/image.webp --description "My image"

# Video
python ingest_video.py --path data/video.mp4 --description "My video"
```

**Query via CLI:**
```bash
python query.py --query "What's in my content?" --top_k 5
```

## ✨ Features

- ✅ Multimodal embeddings (text + images + video in same space)
- ✅ Claude Sonnet with RAG context
- ✅ Real-time chat UI
- ✅ Source attribution with relevance scores
- ✅ Automatic text chunking
- ✅ Batch video frame sampling
- ✅ Cost-optimized (768-dim embeddings)
