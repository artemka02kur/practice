import os
import imagehash
from PIL import Image
import logging
from collections import Counter
import sys
import cv2
import numpy as np


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_folder_images_paths(folder):
    supported_formats = ('.jpeg', '.jpg', '.png', '.bmp', '.gif')
    paths = set()
    for filename in os.listdir(folder):
        if filename.lower().endswith(supported_formats):
            img_path = os.path.join(folder, filename)
            paths.add(img_path)
    logging.info(f"Found image paths in {folder}: {paths}")
    return paths


def compute_hash(image):
    return imagehash.phash(image)


def find_duplicates(folders):
    result = []
    all_hashes = []
    hashes_paths = []
    if not folders:
        return []

    for folder in folders:
        images_hashes, duplicates = process_folder(folder)
        result += duplicates
        all_hashes += list(images_hashes.keys())
        for key, value in images_hashes.items():
            hashes_paths.append((key, value))

    count_duplicates = Counter(all_hashes)

    for image_hash, number_duplicates in count_duplicates.items():
        if number_duplicates > 1:
            image_duplicate = []
            logging.info(f"found: {number_duplicates} duplcates ")
            for hash_path in hashes_paths:
                if hash_path[0] == image_hash:
                    logging.info(f"found: {hash_path[1]} path")
                    image_duplicate.append(hash_path[1])
            result.append(image_duplicate)
    logging.info(f"result: {result} ")
    return result

def process_folder(folder):
    duplicates = []
    images_hashes = {}
    if not os.path.exists(folder):
        logging.warning(f"Folder not found: {folder}")
        return {}, []
    paths = get_folder_images_paths(folder)
    for path in paths:
        try:
            with Image.open(path) as img:
                hash_val = compute_hash(img)
                if hash_val in images_hashes:
                    logging.info(f"Duplicates found: {path} and {images_hashes[hash_val]}")
                    duplicates.append([images_hashes[hash_val], path])
                images_hashes[hash_val] = path
        except Exception as e:
            logging.warning(f"Error processing image {path}: {e}")
    return images_hashes, duplicates


def display_duplicates(duplicates):
    for duplicate_group in duplicates:
        logging.info("Duplicate images:")
        for img_path in duplicate_group:
            logging.info(f"{img_path}")

def visualize_duplicates(duplicates):
    for duplicate_group in duplicates:
        images = []
        for img_path in duplicate_group:
            if not isinstance(img_path, str):
                logging.warning(f"Invalid image path type: {type(img_path)}")
                continue
            if not os.path.exists(img_path):
                logging.warning(f"Image path does not exist: {img_path}")
                continue
            img = cv2.imread(img_path)
            if img is None:
                logging.warning(f"Failed to load image: {img_path}")
                continue
            images.append((img_path, img))

        if images:
            max_height = max(img.shape[0] for _, img in images)
            total_width = sum(img.shape[1] for _, img in images)
            combined_img = np.zeros((max_height, total_width, 3), dtype=np.uint8)

            current_x = 0
            for img_path, img in images:
                height, width = img.shape[:2]
                combined_img[0:height, current_x:current_x + width] = img
                current_x += width

            cv2.imshow('Duplicate Images', combined_img)
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
