import argparse
import hashlib
from pathlib import Path
from embeddings import text_embed
from pinecone_db import PineconeDB

def chunk_text(text: str, chunk_size: int = 2000) -> list:
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def ingest_text(text: str = None, file_path: str = None, custom_id: str = None):
    if text is None and file_path is None:
        raise ValueError("Either --text or --file must be provided")

    if text is not None:
        content = text
        source = "inline"
    else:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        source = str(file_path)

    chunks = chunk_text(content)
    db = PineconeDB()

    items_to_upsert = []
    for chunk_idx, chunk in enumerate(chunks):
        embedding = text_embed(chunk)

        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()[:8]
        if custom_id:
            vector_id = f"{custom_id}_{chunk_idx}"
        else:
            vector_id = f"{source.replace('/', '_')}_{chunk_idx}_{chunk_hash}"

        items_to_upsert.append({
            "id": vector_id,
            "embedding": embedding,
            "metadata": {
                "content_type": "text",
                "source": source,
                "chunk_idx": chunk_idx,
                "text": chunk
            }
        })

    db.upsert_batch(items_to_upsert)

    print(f"Ingested {len(chunks)} text chunk(s) from '{source}'")
    return len(chunks)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest text into Pinecone")
    parser.add_argument("--text", type=str, help="Inline text to embed")
    parser.add_argument("--file", type=str, help="Path to text file to embed")
    parser.add_argument("--id", type=str, help="Custom ID prefix for vectors")

    args = parser.parse_args()

    ingest_text(text=args.text, file_path=args.file, custom_id=args.id)
