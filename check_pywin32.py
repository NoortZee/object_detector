"""
Скрипт для проверки работоспособности библиотеки pywin32
"""

import os
import sys
import traceback

def check_installed_modules():
    """Проверяет установленные модули"""
    print("Проверка установленных модулей...")
    try:
        import pip
        print("pip установлен")
        
        # Проверка версии pip
        import pkg_resources
        pip_version = pkg_resources.get_distribution("pip").version
        print(f"Версия pip: {pip_version}")
        
        # Получение списка установленных пакетов
        installed_packages = [pkg.key for pkg in pkg_resources.working_set]
        
        # Проверка наличия pywin32
        if "pywin32" in installed_packages:
            print("pywin32 установлен")
            
            # Проверка версии pywin32
            pywin32_version = pkg_resources.get_distribution("pywin32").version
            print(f"Версия pywin32: {pywin32_version}")
        else:
            print("ВНИМАНИЕ: pywin32 не установлен!")
            print("Установите его с помощью команды: py -m pip install pywin32")
        
        # Проверка наличия других необходимых пакетов
        for package in ["opencv-python", "numpy", "pyautogui", "pillow"]:
            if package in installed_packages:
                print(f"{package} установлен")
            else:
                print(f"ВНИМАНИЕ: {package} не установлен!")
    except Exception as e:
        print(f"Ошибка при проверке модулей: {e}")
        traceback.print_exc()

def check_win32gui():
    """Проверяет работоспособность модуля win32gui"""
    print("\nПроверка модуля win32gui...")
    try:
        import win32gui
        import win32con
        print("Модуль win32gui импортирован успешно")
        
        # Вывод списка окон верхнего уровня
        windows = []
        
        def enum_windows_callback(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title:
                    windows.append((hwnd, window_title))
            return True
        
        try:
            print("Попытка перечислить окна...")
            win32gui.EnumWindows(enum_windows_callback, None)
            print(f"Найдено {len(windows)} видимых окон")
            
            # Выводим первые 5 окон
            print("Первые 5 окон:")
            for i, (hwnd, title) in enumerate(windows[:5]):
                print(f"  {hwnd}: {title}")
                
            return True
        except Exception as e:
            print(f"ОШИБКА при перечислении окон: {e}")
            traceback.print_exc()
            return False
    except ImportError:
        print("ОШИБКА: Не удалось импортировать win32gui")
        print("Убедитесь, что pywin32 установлен корректно")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        traceback.print_exc()
        return False

def check_system():
    """Проверка системной информации"""
    print("\nСистемная информация:")
    print(f"Версия Python: {sys.version}")
    print(f"Архитектура Python: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    print(f"Платформа: {sys.platform}")
    
    # Проверка пути к Python
    python_path = sys.executable
    print(f"Путь к Python: {python_path}")
    
    # Проверка директорий sys.path
    print("\nПути поиска модулей (sys.path):")
    for i, path in enumerate(sys.path):
        print(f"  {i+1}. {path}")

def repair_pywin32():
    """Попытка исправить проблемы с pywin32"""
    print("\nПопытка исправить проблемы с pywin32...")
    try:
        import os
        import subprocess
        
        # Проверка наличия Python Scripts директории
        python_dir = os.path.dirname(sys.executable)
        scripts_dir = os.path.join(python_dir, "Scripts")
        
        if os.path.exists(scripts_dir):
            print(f"Директория Scripts найдена: {scripts_dir}")
            
            # Поиск pywin32_postinstall.py
            postinstall_script = os.path.join(scripts_dir, "pywin32_postinstall.py")
            
            if os.path.exists(postinstall_script):
                print(f"Найден скрипт postinstall: {postinstall_script}")
                print("Запуск скрипта pywin32_postinstall.py для исправления установки...")
                
                try:
                    # Запуск скрипта с правами администратора
                    result = subprocess.run([sys.executable, postinstall_script, "-install"], 
                                           capture_output=True, text=True)
                    
                    print("Результат выполнения:")
                    print(result.stdout)
                    
                    if result.returncode == 0:
                        print("Скрипт выполнен успешно!")
                        return True
                    else:
                        print(f"Ошибка при выполнении скрипта: {result.stderr}")
                        print("Попробуйте запустить скрипт вручную с правами администратора:")
                        print(f"{sys.executable} {postinstall_script} -install")
                except Exception as e:
                    print(f"Ошибка при запуске скрипта: {e}")
            else:
                print("Скрипт pywin32_postinstall.py не найден")
                print("Переустановите pywin32 с помощью команды:")
                print("py -m pip install --upgrade --force-reinstall pywin32")
        else:
            print(f"Директория Scripts не найдена: {scripts_dir}")
            
        return False
    except Exception as e:
        print(f"Ошибка при попытке исправления: {e}")
        return False

def main():
    print("=== Проверка библиотеки pywin32 ===")
    print("Этот скрипт проверяет правильность установки pywin32 и возможные проблемы")
    
    # Проверка системной информации
    check_system()
    
    # Проверка установленных модулей
    check_installed_modules()
    
    # Проверка win32gui
    win32gui_works = check_win32gui()
    
    # Если win32gui не работает, пытаемся исправить
    if not win32gui_works:
        print("\nОбнаружены проблемы с win32gui! Возможные решения:")
        print("1. Переустановить библиотеку pywin32:")
        print("   py -m pip install --upgrade --force-reinstall pywin32")
        print("2. Запустить скрипт pywin32_postinstall.py с правами администратора")
        
        print("\nПопытаться автоматически исправить проблему? (y/n)")
        answer = input("> ")
        
        if answer.lower() in ["y", "yes", "да", "д"]:
            repair_pywin32()
        else:
            print("Автоматическое исправление пропущено")
    
    print("\n=== Проверка завершена ===")
    print("Если проблемы сохраняются, попробуйте запустить программу с упрощенной версией уведомлений")
    print("или использовать заглушку для notification.py")
    input("Нажмите Enter для выхода...")

 