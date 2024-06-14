import os
import cv2
import imagehash
from PIL import Image
import matplotlib.pyplot as plt
from collections import defaultdict


def load_images_from_folder(folder):
    images = []
    for filename in os.listdir(folder):
        img_path = os.path.join(folder, filename)
        try:
            img = Image.open(img_path)
            images.append((filename, img))
        except Exception as e:
            print(f"Could not open image {img_path}: {e}")
    return images


def compute_hash(image):
    return imagehash.phash(image)


def find_duplicates(folders):
    hashes = defaultdict(list)

    for folder in folders:
        if not os.path.exists(folder):
            print(f"Folder not found: {folder}")
            continue

        images = load_images_from_folder(folder)
        for name, img in images:
            hash_val = compute_hash(img)
            hashes[hash_val].append((folder, name))

    duplicates = {h: files for h, files in hashes.items() if len(files) > 1}
    return duplicates


def display_duplicates(duplicates):
    for hash_val, files in duplicates.items():
        print(f"Duplicate hash {hash_val}:")
        for folder, name in files:
            img_path = os.path.join(folder, name)
            print(f"{img_path}")


if __name__ == "__main__":
    # Получаем абсолютный путь к текущему скрипту
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Формируем относительные пути к папкам с изображениями внутри venv
    folder1 = os.path.join(script_dir, 'venv', 'images1')
    folder2 = os.path.join(script_dir, 'venv', 'Lotus')
    folder3 = os.path.join(script_dir, 'venv', 'Orchid')
    folder4 = os.path.join(script_dir, 'venv', 'Sunflower')
    folder5 = os.path.join(script_dir, 'venv', 'Tulip')
    folder6 = os.path.join(script_dir, 'venv', 'Lilly')

    # Передаем список папок в функцию find_duplicates
    folders = [folder1, folder2, folder3, folder4, folder5, folder6]

    # Вызываем функцию поиска дубликатов с одним аргументом - списком папок
    duplicates = find_duplicates(folders)

    if duplicates:
        print("Duplicate images found:")
        display_duplicates(duplicates)
    else:
        print("No duplicate images found.")
