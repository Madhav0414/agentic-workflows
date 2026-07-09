import argparse
from pathlib import Path
from embeddings import image_embed
from pinecone_db import PineconeDB

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".heic", ".heif", ".avif"}

def ingest_images(file_path: str = None, directory: str = None, description: str = ""):
    if file_path is None and directory is None:
        raise ValueError("Either --path or --dir must be provided")

    db = PineconeDB()
    images_to_process = []

    if file_path:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        images_to_process.append((file_path, description))

    if directory:
        dir_path = Path(directory)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        for ext in SUPPORTED_FORMATS:
            images_to_process.extend([
                (img_path, "")
                for img_path in dir_path.glob(f"*{ext}")
            ])
            images_to_process.extend([
                (img_path, "")
                for img_path in dir_path.glob(f"*{ext.upper()}")
            ])

    items_to_upsert = []
    for image_path, img_description in images_to_process:
        try:
            embedding = image_embed(str(image_path))

            vector_id = f"img_{image_path.stem}"
            items_to_upsert.append({
                "id": vector_id,
                "embedding": embedding,
                "metadata": {
                    "content_type": "image",
                    "source": str(image_path),
                    "description": img_description or image_path.name
                }
            })
        except Exception as e:
            print(f"Error embedding {image_path}: {e}")

    if items_to_upsert:
        db.upsert_batch(items_to_upsert)
        print(f"Ingested {len(items_to_upsert)} image(s)")
    else:
        print("No images ingested.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest images into Pinecone")
    parser.add_argument("--path", type=str, help="Path to single image file")
    parser.add_argument("--dir", type=str, help="Directory of images to ingest")
    parser.add_argument("--description", type=str, default="", help="Description for single image")

    args = parser.parse_args()

    ingest_images(file_path=args.path, directory=args.dir, description=args.description)
