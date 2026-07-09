from pinecone import Pinecone
from config import PINECONE_API_KEY, INDEX_NAME

class PineconeDB:
    def __init__(self):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index = self.pc.Index(INDEX_NAME)

    def upsert_one(self, id: str, embedding: list, metadata: dict):
        self.index.upsert(
            vectors=[
                {
                    "id": id,
                    "values": embedding,
                    "metadata": metadata
                }
            ]
        )

    def upsert_batch(self, items: list):
        vectors = []
        for item in items:
            vectors.append({
                "id": item["id"],
                "values": item["embedding"],
                "metadata": item["metadata"]
            })

            if len(vectors) >= 100:
                self.index.upsert(vectors=vectors)
                vectors = []

        if vectors:
            self.index.upsert(vectors=vectors)

    def search(self, query_embedding: list, top_k: int = 5, filter=None) -> list:
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )

        return [
            {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata
            }
            for match in results.matches
        ]
