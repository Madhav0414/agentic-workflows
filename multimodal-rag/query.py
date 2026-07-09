import argparse
from embeddings import text_embed
from pinecone_db import PineconeDB
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL

def query_rag(query_text: str, top_k: int = 5):
    db = PineconeDB()
    query_embedding = text_embed(query_text)
    results = db.search(query_embedding, top_k=top_k)

    if not results:
        print("No results found.")
        return

    context_parts = []
    references = []

    for result in results:
        metadata = result["metadata"]
        content_type = metadata.get("content_type", "unknown")
        source = metadata.get("source", "unknown")
        score = result["score"]

        if content_type == "text":
            text = metadata.get("text", "")
            context_parts.append(f"[{source} (score: {score:.3f})]\n{text}")
            references.append(f"- {source} (relevance: {score:.3f})")
        elif content_type == "image":
            description = metadata.get("description", "No description")
            context_parts.append(f"[IMAGE from {source}]\n{description}")
            references.append(f"- Image from {source} (relevance: {score:.3f})")
        elif content_type == "video":
            description = metadata.get("description", "No description")
            context_parts.append(f"[VIDEO from {source}]\n{description}")
            references.append(f"- Video from {source} (relevance: {score:.3f})")

    context = "\n\n---\n\n".join(context_parts)

    system_prompt = "You are a helpful assistant. Answer questions based on the provided context. If the context doesn't contain relevant information, say so."
    user_prompt = f"""Context:
{context}

Question: {query_text}

Please answer based on the context above."""

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    answer = response.choices[0].message.content

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(answer)
    print("\n" + "=" * 60)
    print("SOURCES")
    print("=" * 60)
    for ref in references:
        print(ref)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query with RAG")
    parser.add_argument("--query", type=str, required=True, help="Query text")
    parser.add_argument("--top_k", type=int, default=5, help="Number of results (default: 5)")

    args = parser.parse_args()
    query_rag(args.query, top_k=args.top_k)
