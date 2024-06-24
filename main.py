import os
import imagehash
from PIL import Image
import logging
from collections import Counter
import sys
import cv2
import numpy as np
from concurrent.futures import ProcessPoolExecutor, as_completed

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Функция для получения путей к изображениям в папке
def get_folder_images_paths(folder):
    supported_formats = ('.jpeg', '.jpg', '.png', '.bmp', '.gif')  # Поддерживаемые форматы изображений
    paths = set()  # Множество для хранения путей к изображениям
    for filename in os.listdir(folder):  # Перебор файлов в папке
        if filename.lower().endswith(supported_formats):  # Проверка формата файла
            img_path = os.path.join(folder, filename)  # Полный путь к изображению
            paths.add(img_path)  # Добавление пути в множество
    logging.info(f"Found image paths in {folder}: {paths}")  # Логирование найденных путей
    return paths

# Функция для вычисления хэша изображения
def compute_hash(image):
    return imagehash.phash(image)  # Использование perceptual hash для вычисления хэша

# Функция для обработки папки и поиска дубликатов изображений
def process_folder(folder):
    duplicates = []  # Список для хранения дубликатов
    images_hashes = {}  # Словарь для хранения хэшей изображений и их путей
    if not os.path.exists(folder):  # Проверка существования папки
        logging.warning(f"Folder not found: {folder}")  # Логирование предупреждения
        return {}, []  # Возвращение пустых значений
    paths = get_folder_images_paths(folder)  # Получение путей к изображениям в папке
    for path in paths:  # Перебор путей к изображениям
        try:
            with Image.open(path) as img:  # Открытие изображения
                hash_val = compute_hash(img)  # Вычисление хэша изображения
                if hash_val in images_hashes:  # Проверка наличия хэша в словаре
                    logging.info(f"Duplicates found: {path} and {images_hashes[hash_val]}")  # Логирование дубликатов
                    duplicates.append([images_hashes[hash_val], path])  # Добавление дубликатов в список
                images_hashes[hash_val] = path  # Добавление хэша и пути в словарь
        except Exception as e:  # Обработка исключений
            logging.warning(f"Error processing image {path}: {e}")  # Логирование ошибок
    return images_hashes, duplicates  # Возвращение словаря хэшей и списка дубликатов

# Функция для поиска дубликатов изображений в нескольких папках
def find_duplicates(folders):
    result = []  # Список для хранения результатов
    all_hashes = []  # Список для хранения всех хэшей
    hashes_paths = []  # Список для хранения хэшей и путей к изображениям

    with ProcessPoolExecutor() as executor:  # Создание пула процессов
        futures = {executor.submit(process_folder, folder): folder for folder in folders}  # Отправка задач в пул процессов
        for future in as_completed(futures):  # Обработка завершенных задач
            folder = futures[future]  # Получение папки, связанной с задачей
            try:
                images_hashes, duplicates = future.result()  # Получение результатов задачи
                result += duplicates  # Добавление дубликатов в общий список
                all_hashes += list(images_hashes.keys())  # Добавление хэшей в общий список
                for key, value in images_hashes.items():  # Перебор хэшей и путей
                    hashes_paths.append((key, value))  # Добавление хэшей и путей в список
            except Exception as exc:  # Обработка исключений
                logging.warning(f"{folder} generated an exception: {exc}")  # Логирование исключений

    count_duplicates = Counter(all_hashes)  # Подсчет количества каждого хэша

    for image_hash, number_duplicates in count_duplicates.items():  # Перебор хэшей и их количества
        if number_duplicates > 1:  # Проверка наличия дубликатов
            image_duplicate = []  # Список для хранения путей к дубликатам
            logging.info(f"Found: {number_duplicates} duplicates ")  # Логирование количества дубликатов
            for hash_path in hashes_paths:  # Перебор хэшей и путей
                if hash_path[0] == image_hash:  # Проверка совпадения хэша
                    logging.info(f"Found: {hash_path[1]} path")  # Логирование пути к дубликату
                    image_duplicate.append(hash_path[1])  # Добавление пути в список дубликатов
            result.append(image_duplicate)  # Добавление списка дубликатов в общий список
    logging.info(f"Result: {result} ")  # Логирование итогового результата
    return result  # Возвращение списка дубликатов

def display_duplicates(duplicates):
    #  Выводит информацию о дубликатах изображений.

    for duplicate_group in duplicates:
        logging.info("Duplicate images:")
        for img_path in duplicate_group:
            logging.info(f"{img_path}")

def visualize_duplicates(duplicates):

  # Визуализирует дубликаты изображений.

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
            os.path.join(script_dir, 'venv', 'image1'),
            os.path.join(script_dir, 'venv', 'Lotus'),
            os.path.join(script_dir, 'venv', 'Orchid'),
            os.path.join(script_dir, 'venv', 'Sunflower'),
            os.path.join(script_dir, 'venv', 'Tulip'),
            os.path.join(script_dir, 'venv', 'Lilly')
        ]

    duplicates = find_duplicates(folders)

    if duplicates:
        logging.info("Duplicates found:")
        display_duplicates(duplicates)
        visualize_duplicates(duplicates)
    else:
        logging.info("Duplicates not found.")
