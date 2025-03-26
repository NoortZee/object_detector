import sys
import os
import importlib.util
import platform
import subprocess
from pathlib import Path

print("=== Проверка окружения для GameDetector ===")

# Получение данных о системе
print(f"\nИнформация о системе:")
print(f"Python версия: {sys.version}")
print(f"Операционная система: {platform.system()} {platform.release()}")
print(f"Текущая директория: {os.getcwd()}")
print(f"Python исполняемый файл: {sys.executable}")

# Проверка наличия нужных файлов
required_files = [
    "game_detector.py",
    "notification.py",
    "color_picker.py",
    "requirements.txt"
]

print("\nПроверка наличия файлов:")
for file in required_files:
    file_exists = os.path.isfile(file)
    print(f"- {file}: {'Найден' if file_exists else 'НЕ НАЙДЕН'}")

# Проверка библиотек
required_packages = [
    "cv2",
    "numpy",
    "PIL",
    "win32gui",
    "tkinter"
]

print("\nПроверка библиотек Python:")
for package in required_packages:
    try:
        if package == "cv2":
            import_name = "opencv-python"
            spec = importlib.util.find_spec("cv2")
        elif package == "PIL":
            import_name = "pillow"
            spec = importlib.util.find_spec("PIL")
        elif package == "win32gui":
            import_name = "pywin32"
            spec = importlib.util.find_spec("win32gui")
        else:
            import_name = package
            spec = importlib.util.find_spec(package)

        if spec is not None:
            mod = importlib.import_module(package)
            try:
                version = mod.__version__
            except AttributeError:
                if package == "cv2":
                    version = mod.CV_VERSION
                elif package == "tkinter":
                    version = f"Python {sys.version_info.major}.{sys.version_info.minor} встроенный"
                else:
                    version = "неизвестно"
            
            print(f"- {package} (как {import_name}): Установлен (версия {version})")
        else:
            print(f"- {package} (как {import_name}): НЕ УСТАНОВЛЕН")
    except ImportError as e:
        print(f"- {package} (как {import_name}): НЕ УСТАНОВЛЕН ({str(e)})")

# Проверка BlueStacks
print("\nПоиск окна BlueStacks:")
try:
    import win32gui
    
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_text = win32gui.GetWindowText(hwnd)
            if "BlueStacks" in window_text:
                windows.append((hwnd, window_text))
        return True
    
    windows = []
    win32gui.EnumWindows(callback, windows)
    
    if windows:
        print("Найдены окна BlueStacks:")
        for i, (hwnd, title) in enumerate(windows, 1):
            rect = win32gui.GetWindowRect(hwnd)
            print(f"  {i}. '{title}' (hwnd: {hwnd}) - {rect}")
    else:
        print("Окна BlueStacks не найдены!")
        print("Убедитесь, что BlueStacks запущен перед запуском программы.")
        
except Exception as e:
    print(f"Ошибка при поиске окон BlueStacks: {str(e)}")

# Проверка прав доступа
print("\nПроверка прав доступа:")
try:
    test_file = "test_permission.txt"
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
    print("- Запись в текущую директорию: OK")
except Exception as e:
    print(f"- Запись в текущую директорию: ОШИБКА ({str(e)})")

# Проверка захвата экрана
print("\nПроверка возможности захвата экрана:")
try:
    from PIL import ImageGrab
    screenshot = ImageGrab.grab()
    test_screenshot = "test_screenshot.png"
    screenshot.save(test_screenshot)
    os.remove(test_screenshot)
    print("- Захват экрана: OK")
except Exception as e:
    print(f"- Захват экрана: ОШИБКА ({str(e)})")

print("\n=== Проверка завершена ===")
print("Если вы видите ошибки в отчете, исправьте их перед запуском программы.")
print("Чтобы запустить программу, выполните: python game_detector.py")
print("\nНажмите Enter для выхода...")
input() 