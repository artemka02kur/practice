import os
import imagehash
from PIL import Image
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import sys
import cv2
import numpy as np


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_images_from_folder(folder):

    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
    images = []
    for filename in os.listdir(folder):
        if filename.lower().endswith(supported_formats):
            img_path = os.path.join(folder, filename)
            try:
                img = Image.open(img_path)
                images.append((filename, img))
            except Exception as e:
                logging.warning(f"Не удалось открыть изображение {img_path}: {e}")
    return images


def compute_hash(image):
    return imagehash.phash(image)


def find_duplicates(folders):
    hashes = defaultdict(list)

    def process_folder(folder):
        if not os.path.exists(folder):
            logging.warning(f"Папка не найдена: {folder}")
            return

        images = load_images_from_folder(folder)
        for name, img in images:
            hash_val = compute_hash(img)
            hashes[hash_val].append((folder, name))

    with ThreadPoolExecutor() as executor:
        executor.map(process_folder, folders)

    duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
    return duplicates


def display_duplicates(duplicates):
    for hash_val, files in duplicates.items():
        logging.info(f"Дубликаты с хэшем {hash_val}:")
        for folder, name in files:
            img_path = os.path.join(folder, name)
            logging.info(f"{img_path}")


def visualize_duplicates(duplicates):
    for hash_val, files in duplicates.items():
        images = []
        for folder, name in files:
            img_path = os.path.join(folder, name)
            img = cv2.imread(img_path)
            if img is not None:
                images.append((name, img))

        if images:
            max_height = max(img.shape[0] for _, img in images)
            total_width = sum(img.shape[1] for _, img in images)
            combined_img = np.zeros((max_height, total_width, 3), dtype=np.uint8)

            current_x = 0
            for name, img in images:
                height, width = img.shape[:2]
                combined_img[0:height, current_x:current_x + width] = img
                current_x += width
            cv2.imshow(f'Duplicates with hash {hash_val}', combined_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        folders = sys.argv[1:]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        folders = [
            os.path.join(script_dir, 'venv', 'images1'),
            os.path.join(script_dir, 'venv', 'Lotus'),
            os.path.join(script_dir, 'venv', 'Orchid'),
            os.path.join(script_dir, 'venv', 'Sunflower'),
            os.path.join(script_dir, 'venv', 'Tulip'),
            os.path.join(script_dir, 'venv', 'Lilly')
        ]

    duplicates = find_duplicates(folders)

    if duplicates:
        logging.info("Найдены дубликаты изображений:")
        display_duplicates(duplicates)
        visualize_duplicates(duplicates)
    else:
        logging.info("Дубликаты изображений не найдены.")
