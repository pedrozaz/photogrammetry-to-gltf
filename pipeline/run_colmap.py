import os
import subprocess
import sqlite3
from pathlib import Path

# LOCAL PATHS
PROJECT_DIR = Path(__file__).resolve().parent.parent
IMAGE_DIR = PROJECT_DIR / "data" / "raw_images"
COLMAP_WORKSPACE = PROJECT_DIR / "pipeline" / "colmap_workspace"
DB_PATH = COLMAP_WORKSPACE / "database.db"
SPARSE_DIR = COLMAP_WORKSPACE / "sparse"

# DOCKER PATHS
DOCKER_IMAGE_DIR = "/workspace/data/raw_images"
DOCKER_WORKSPACE = "/workspace/pipeline/colmap_workspace"
DOCKER_DB_PATH = f"{DOCKER_WORKSPACE}/database.db"
DOCKER_SPARSE_DIR = f"{DOCKER_WORKSPACE}/sparse"

def run_colmap(args):
    cmd = [
        'docker', 'run', '--rm',
        '--gpus', 'all',
        '-v', f'{PROJECT_DIR}:/workspace',
        'colmap/colmap:latest', 'colmap'
    ] + args
    print(f'\n[EXEC] {" ".join(cmd)}')
    subprocess.run(cmd, check=True)

def verify_registration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM images')
    total_images = cursor.fetchone()[0]
    conn.close()

    model_0_dir = SPARSE_DIR / "0"
    if model_0_dir.exists():
        # Read the cameras.txt or use model_analyzer to check registration
        cmd = [
            'docker', 'run', '--rm',
            '-v', f'{PROJECT_DIR}:/workspace',
            'colmap/colmap:latest', 'colmap', 'model_analyzer',
            '--path', f'{DOCKER_SPARSE_DIR}/0'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        for line in result.stdout.split('\n'):
            if 'Registered images:' in line:
                registered = int(line.split()[2])
                percent = (registered / total_images) * 100
                print(f'\n--- Reconstruction Result ---')
                print(f'Total images: {total_images}')
                print(f'Registered images: {registered} ({percent:.2f}%)')

                if percent >= 70:
                    print('[SUCCESS] Registration criteria met. Ready for Dense Reconstruction.')
                else:
                    print('[WARNING] Less than 70% of images were registered. Recapture required.')
                break

    else:
        print('\n[ERROR] Reconstructed model (directory 0) not found.')

def main():
    COLMAP_WORKSPACE.mkdir(parents=True, exist_ok=True)
    SPARSE_DIR.mkdir(parents=True, exist_ok=True)

    if not any(IMAGE_DIR.iterdir()):
        print(f'\n[ERROR] Image directory not found in {IMAGE_DIR}.')
        return

    # Feature Extraction
    run_colmap([
        'feature_extractor',
        '--database_path', DOCKER_DB_PATH,
        '--image_path', DOCKER_IMAGE_DIR,
        '--ImageReader.single_camera', '1'
        ])

    # Exhaustive Matching
    run_colmap([
        'exhaustive_matcher',
        '--database_path', DOCKER_DB_PATH
    ])

    # Sparse Reconstruction (Mapping)
    run_colmap([
        'mapper',
        '--database_path', DOCKER_DB_PATH,
        '--image_path', DOCKER_IMAGE_DIR,
        '--output_path', DOCKER_SPARSE_DIR
    ])

    # Validation
    verify_registration()

if __name__ == '__main__':
    main()

