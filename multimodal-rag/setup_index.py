from pinecone import Pinecone
from config import PINECONE_API_KEY, INDEX_NAME, EMBEDDING_DIM, METRIC

def setup_pinecone_index():
    pc = Pinecone(api_key=PINECONE_API_KEY)

    existing_indexes = [idx.name for idx in pc.list_indexes()]

    if INDEX_NAME in existing_indexes:
        print(f"Index '{INDEX_NAME}' already exists.")
        return

    print(f"Creating index '{INDEX_NAME}' with dimension={EMBEDDING_DIM}, metric={METRIC}...")

    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric=METRIC,
        spec={
            "serverless": {
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    )

    print(f"Index '{INDEX_NAME}' created successfully.")

if __name__ == "__main__":
    setup_pinecone_index()
