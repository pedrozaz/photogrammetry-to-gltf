from pathlib import Path
from PIL import Image

PROJECT_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_DIR / "data" / "raw_images"
MAX_DIMENSION = 1600

def resize_images():
    images = list(IMAGE_DIR.glob("*.jpg")) + list(IMAGE_DIR.glob("*.jpeg"))

    if not images:
        print("No images found")
        return

    print("Resizing images...")
    for img_path in images:
        try:
            with Image.open(img_path) as img:
                img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
                img.save(img_path, "JPEG", quality=90)
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

    print("Done")

if __name__ == "__main__":
    resize_images()