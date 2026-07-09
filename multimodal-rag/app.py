from flask import Flask, render_template, request, jsonify
from embeddings import text_embed
from pinecone_db import PineconeDB
from config import get_genai_client
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai_client = get_genai_client()
db = PineconeDB()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    try:
        logger.info(f"Processing message: {user_message[:50]}...")

        logger.info("Embedding query...")
        query_embedding = text_embed(user_message)

        logger.info("Searching Pinecone...")
        results = db.search(query_embedding, top_k=5)

        context_parts = []
        references = []

        for result in results:
            metadata = result["metadata"]
            content_type = metadata.get("content_type", "unknown")
            source = metadata.get("source", "unknown").split("/")[-1]
            score = result["score"]

            if content_type == "text":
                text = metadata.get("text", "")[:500]
                context_parts.append(f"[{source}]\n{text}")
                references.append({
                    "source": source,
                    "type": "text",
                    "score": round(score, 3)
                })
            elif content_type == "image":
                description = metadata.get("description", "No description")
                context_parts.append(f"[IMAGE: {source}]\n{description}")
                references.append({
                    "source": source,
                    "type": "image",
                    "score": round(score, 3)
                })
            elif content_type == "video":
                description = metadata.get("description", "No description")
                context_parts.append(f"[VIDEO: {source}]\n{description}")
                references.append({
                    "source": source,
                    "type": "video",
                    "score": round(score, 3)
                })

        context = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant context found."

        full_prompt = f"""You are an expert assistant analyzing user-provided content (text documents, images, and videos).

IMPORTANT: You MUST answer based ONLY on the retrieved context below. Do not use general knowledge unless the context is empty.

Retrieved Context from Knowledge Base:
{context}

User Question: {user_message}

Instructions:
1. Answer directly using ONLY the information in the retrieved context
2. Be specific and detailed - reference exact details from the content
3. If asked about something not in the context, say "The provided context does not contain information about..."
4. Keep answers concise but informative

Answer:"""

        logger.info("Calling Gemini 2.5 Flash...")
        response = genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt,
            config={"max_output_tokens": 2048}
        )

        answer = response.text

        return jsonify({
            "answer": answer,
            "references": references,
            "context_available": len(context_parts) > 0
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="localhost", port=5000, threaded=True)
