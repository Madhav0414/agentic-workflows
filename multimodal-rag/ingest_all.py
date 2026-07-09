import sys
from pathlib import Path
from ingest_text import ingest_text
from ingest_images import ingest_images
from ingest_video import ingest_video

def ingest_all_from_data():
    data_dir = Path("data")

    if not data_dir.exists():
        print(f"Error: {data_dir} directory not found")
        return

    text_files = list(data_dir.glob("*.txt"))
    image_files = list(data_dir.glob("*.webp")) + list(data_dir.glob("*.png")) + list(data_dir.glob("*.jpg")) + list(data_dir.glob("*.jpeg"))
    video_files = list(data_dir.glob("*.mp4")) + list(data_dir.glob("*.mov")) + list(data_dir.glob("*.mpeg"))

    print(f"Found {len(text_files)} text files, {len(image_files)} images, {len(video_files)} videos")

    total_ingested = 0

    # Ingest text files
    for text_file in text_files:
        try:
            count = ingest_text(file_path=str(text_file), custom_id=text_file.stem)
            total_ingested += count
        except Exception as e:
            print(f"Error ingesting {text_file}: {e}")

    # Ingest images
    if image_files:
        try:
            ingest_images(directory=str(data_dir))
            total_ingested += len(image_files)
        except Exception as e:
            print(f"Error ingesting images: {e}")

    # Ingest videos
    for video_file in video_files:
        try:
            ingest_video(str(video_file), description=video_file.stem)
            total_ingested += 1
        except Exception as e:
            print(f"Error ingesting {video_file}: {e}")

    print(f"\n[OK] Total items ingested: {total_ingested}")

if __name__ == "__main__":
    ingest_all_from_data()
