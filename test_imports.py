"""
Скрипт для тестирования импортов всех необходимых модулей
и библиотек для работы программы обнаружения объектов в игре.
"""

print("Тестирование импортов...")

try:
    import cv2
    print("✓ opencv-python (cv2) успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта opencv-python (cv2): {e}")

try:
    import numpy as np
    print("✓ numpy успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта numpy: {e}")

try:
    import pyautogui
    print("✓ pyautogui успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта pyautogui: {e}")

try:
    from PIL import Image, ImageGrab
    print("✓ PIL (Pillow) успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта PIL (Pillow): {e}")

try:
    import win32gui
    import win32con
    import win32ui
    print("✓ pywin32 (win32gui, win32con, win32ui) успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта pywin32: {e}")

try:
    import tkinter as tk
    from tkinter import font
    print("✓ tkinter успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта tkinter: {e}")

try:
    import logging
    print("✓ logging успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта logging: {e}")

try:
    import time
    print("✓ time успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта time: {e}")

try:
    import threading
    print("✓ threading успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта threading: {e}")

try:
    import os
    print("✓ os успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта os: {e}")

try:
    import json
    print("✓ json успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта json: {e}")

try:
    import winsound
    print("✓ winsound успешно импортирован")
except ImportError as e:
    print(f"✗ Ошибка импорта winsound: {e}")

print("\nПроверка импорта локальных модулей...")

try:
    # Сначала проверим наличие файлов
    notification_exists = os.path.isfile("notification.py")
    if notification_exists:
        # Только если файл существует, пробуем импортировать
        try:
            from notification import GameNotification
            print("✓ notification.py (GameNotification) успешно импортирован")
        except Exception as e:
            print(f"✗ Ошибка импорта из notification.py: {e}")
    else:
        print("✗ Файл notification.py не найден")
except Exception as e:
    print(f"✗ Ошибка при проверке notification.py: {e}")

print("\nИмпорты проверены. Если вы видите ошибки выше, установите недостающие библиотеки.")
print("Для установки библиотек используйте команду: pip install -r requirements.txt")
print("\nНажмите Enter для выхода...")
input() 