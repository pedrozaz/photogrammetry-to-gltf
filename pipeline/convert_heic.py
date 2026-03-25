from pathlib import Path
from PIL import Image
import pillow_heif

PROJECT_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_DIR / 'data' / 'raw_images'

def convert_heic_to_jpg():
    pillow_heif.register_heif_opener()
    heic_files = list(IMAGE_DIR.glob('*.heic')) + list(IMAGE_DIR.glob('*.HEIC'))

    if not heic_files:
        print("No HEIC files found in the directory.")
        return

    print(f"Found {len(heic_files)} HEIC files. Starting conversion...")
    for file_path in heic_files:
        try:
            img = Image.open(file_path)
            jpg_path = file_path.with_suffix('.jpg')
            img.save(jpg_path, 'JPEG', quality=95)
            file_path.unlink()
        except Exception as e:
            print(f"Error converting {file_path}: {e}")

    print("Conversion completed. All HEIC files have been converted to JPG.")

if __name__ == "__main__":
    convert_heic_to_jpg()

