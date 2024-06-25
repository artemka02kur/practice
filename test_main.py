import os
import pytest
import numpy as np
from main import get_folder_images_paths, compute_hash, process_folder, find_duplicates
from PIL import Image


def test_find_duplicates_not_found_in_one_folder():
    # Настоящий тест с использованием реальных изображений из папок image1 и image2
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folders = [os.path.join(script_dir, 'venv', 'image1')]
    duplicates = find_duplicates(folders)
    assert duplicates == []


def test_find_duplicates_found_in_one_folder():
    # Настоящий тест с использованием реальных изображений из папок image1 и image2
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folders = [os.path.join(script_dir, 'venv', 'images2')]
    duplicates = find_duplicates(folders)
    assert len(duplicates) == 1
    assert len(duplicates[0]) == 2
    assert "C:\\Users\\artem\\OneDrive\\Documents\\GitHub\\practice-1\\venv\\images2\\rtyuj.png" in duplicates[0]
    assert "C:\\Users\\artem\\OneDrive\\Documents\\GitHub\\practice-1\\venv\\images2\\202535.png" in duplicates[0]


def test_find_duplicates_found_in_two_folders():
    # Настоящий тест с использованием реальных изображений из папок image1 и image2
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folders = [os.path.join(script_dir, 'venv', 'images2'), os.path.join(script_dir, 'venv', 'images1')]
    duplicates = find_duplicates(folders)
    assert len(duplicates) == 2
    assert len(duplicates[0]) == 2
    assert len(duplicates[1]) == 2
    assert "C:\\Users\\artem\\OneDrive\\Documents\\GitHub\\practice-1\\venv\\images2\\98.jpg" in duplicates[1]
    assert "C:\\Users\\artem\\OneDrive\\Documents\\GitHub\\practice-1\\venv\\images1\\1.jpg" in duplicates[1]
    assert "C:\\Users\\artem\\OneDrive\\Documents\\GitHub\\practice-1\\venv\\images2\\rtyuj.png" in duplicates[0]
    assert "C:\\Users\\artem\\OneDrive\\Documents\\GitHub\\practice-1\\venv\\images2\\202535.png" in duplicates[0]


def test_find_duplicates_no_folders():
    duplicates = find_duplicates([])
    assert duplicates == []


if __name__ == "__main__":
    pytest.main()
