import argparse
from pathlib import Path
from embeddings import video_embed, generate_video_description
from pinecone_db import PineconeDB

def ingest_video(video_path: str, description: str = ""):
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    db = PineconeDB()

    try:
        print(f"Embedding video: {video_path}")
        embedding = video_embed(str(video_path))

        if not description:
            print(f"Generating description for video: {video_path}")
            description = generate_video_description(str(video_path))
            print(f"Generated description: {description}")

        vector_id = f"vid_{video_path.stem}"
        db.upsert_one(
            id=vector_id,
            embedding=embedding,
            metadata={
                "content_type": "video",
                "source": str(video_path),
                "description": description
            }
        )

        print(f"Ingested video: {video_path}")
    except Exception as e:
        print(f"Error embedding video: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest video into Pinecone")
    parser.add_argument("--path", type=str, required=True, help="Path to video file")
    parser.add_argument("--description", type=str, default="", help="Description of video")

    args = parser.parse_args()

    ingest_video(args.path, description=args.description)
