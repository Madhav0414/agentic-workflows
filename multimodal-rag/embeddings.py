import cv2
from pathlib import Path
from google import genai
from google.genai import types
from config import get_genai_client, EMBEDDING_MODEL, EMBEDDING_DIM

def text_embed(text: str) -> list:
    client = get_genai_client()
    task_prefix = "task: retrieval | text: "
    prefixed_text = task_prefix + text

    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=prefixed_text,
        config={"output_dimensionality": EMBEDDING_DIM}
    )

    return result.embeddings[0].values

def image_embed(image_path: str) -> list:
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    ext = image_path.suffix.lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".heic": "image/heic",
        ".heif": "image/heif",
        ".avif": "image/avif"
    }

    mime_type = mime_map.get(ext, "image/png")

    client = get_genai_client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[
            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            )
        ],
        config={"output_dimensionality": EMBEDDING_DIM}
    )

    return result.embeddings[0].values

def video_embed(video_path: str, max_frames: int = 6) -> list:
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if frame_count == 0:
        raise ValueError(f"Video has no frames: {video_path}")

    sample_indices = [
        int(i * (frame_count - 1) / (max_frames - 1))
        for i in range(max_frames)
    ] if frame_count > 1 else [0]

    cap = cv2.VideoCapture(str(video_path))
    frames_bytes = []
    frame_idx = 0
    sample_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if sample_idx < len(sample_indices) and frame_idx == sample_indices[sample_idx]:
            _, buffer = cv2.imencode(".jpg", frame)
            frames_bytes.append(buffer.tobytes())
            sample_idx += 1

        frame_idx += 1

    cap.release()

    if not frames_bytes:
        raise ValueError(f"No frames extracted from video: {video_path}")

    parts = [
        types.Part.from_bytes(data=frame_data, mime_type="image/jpeg")
        for frame_data in frames_bytes
    ]

    client = get_genai_client()
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=parts,
        config={"output_dimensionality": EMBEDDING_DIM}
    )

    return result.embeddings[0].values

def generate_video_description(video_path: str, max_frames: int = 6) -> str:
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    if frame_count == 0:
        raise ValueError(f"Video has no frames: {video_path}")

    sample_indices = [
        int(i * (frame_count - 1) / (max_frames - 1))
        for i in range(max_frames)
    ] if frame_count > 1 else [0]

    cap = cv2.VideoCapture(str(video_path))
    frames_bytes = []
    frame_idx = 0
    sample_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if sample_idx < len(sample_indices) and frame_idx == sample_indices[sample_idx]:
            _, buffer = cv2.imencode(".jpg", frame)
            frames_bytes.append(buffer.tobytes())
            sample_idx += 1

        frame_idx += 1

    cap.release()

    if not frames_bytes:
        raise ValueError(f"No frames extracted from video: {video_path}")

    parts = [
        types.Part.from_text(text="Analyze these video frames and provide a concise description of what the video is about. Be specific about the content, activities, and any important details you can see. Keep it to 2-3 sentences.")
    ]

    parts.extend([
        types.Part.from_bytes(data=frame_data, mime_type="image/jpeg")
        for frame_data in frames_bytes
    ])

    client = get_genai_client()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=parts
    )

    return response.text
