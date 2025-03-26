"""
Отладочный скрипт для запуска game_detector.py с подробным выводом ошибок
"""

import os
import sys
import logging
import platform
import traceback
from time import sleep

def setup_logging():
    """Настройка расширенного логирования для отладки"""
    # Создание директории для логов, если её нет
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Настройка логирования в файл с максимальным уровнем детализации
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='logs/debug.log',
        filemode='w'
    )
    
    # Добавляем вывод в консоль
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    
    logging.info("Логирование настроено")

def check_system():
    """Проверка системы и окружения"""
    logging.info("=== Информация о системе ===")
    logging.info(f"Платформа: {platform.platform()}")
    logging.info(f"Python версия: {platform.python_version()}")
    logging.info(f"Процессор: {platform.processor()}")
    
    # Проверяем переменные окружения
    logging.info("=== Переменные окружения ===")
    for var in ['PYTHONPATH', 'PATH']:
        logging.info(f"{var}: {os.environ.get(var, 'не установлена')}")
    
    # Проверяем наличие необходимых модулей
    logging.info("=== Проверка модулей ===")
    required_modules = [
        'cv2', 'numpy', 'PIL', 'pyautogui', 'msvcrt'
    ]
    
    optional_modules = [
        'win32gui', 'win32con', 'win32ui', 'win32process', 'ctypes'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            logging.info(f"✓ Модуль {module} доступен")
        except ImportError:
            logging.critical(f"✗ Модуль {module} НЕ НАЙДЕН - программа не сможет работать!")
    
    for module in optional_modules:
        try:
            __import__(module)
            logging.info(f"✓ Опциональный модуль {module} доступен")
        except ImportError:
            logging.warning(f"✗ Опциональный модуль {module} не найден")
    
    # Проверяем наличие необходимых файлов
    logging.info("=== Проверка файлов ===")
    required_files = [
        'game_detector.py', 
    ]
    
    for file in required_files:
        if os.path.exists(file):
            logging.info(f"✓ Файл {file} найден ({os.path.getsize(file)} байт)")
        else:
            logging.critical(f"✗ Файл {file} НЕ НАЙДЕН!")

def run_with_debug():
    """Запуск программы с перехватом всех исключений"""
    try:
        logging.info("Запуск программы в режиме отладки...")
        
        # Импортируем основной модуль
        from game_detector import GameDetector
        
        # Создаем экземпляр и запускаем
        detector = GameDetector()
        
        # Устанавливаем расширенный вывод для отладки
        logging.info("Запуск основного цикла программы...")
        detector.run()
    
    except Exception as e:
        logging.critical(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logging.critical("Подробная информация об ошибке:")
        logging.critical(traceback.format_exc())
        print("\n\n========== КРИТИЧЕСКАЯ ОШИБКА ==========")
        print(f"Ошибка: {e}")
        print("\nСтек вызовов:")
        print(traceback.format_exc())
        print("\nПроверьте файл logs/debug.log для получения полной информации об ошибке.")
        print("=========================================\n")
        
        # Делаем паузу, чтобы пользователь мог прочитать сообщение об ошибке
        print("Нажмите ENTER для выхода...")
        input()
        return False
    
    return True

if __name__ == "__main__":
    print("===============================")
    print("=== ЗАПУСК В РЕЖИМЕ ОТЛАДКИ ===")
    print("===============================")
    print("Этот режим предоставляет расширенную информацию для диагностики проблем.")
    print("Полный журнал работы программы будет сохранен в файле logs/debug.log.")
    print()
    
    # Инициализируем логирование
    setup_logging()
    
    # Проверяем систему
    check_system()
    
    # Запускаем программу
    print("\nЗапуск программы...")
    result = run_with_debug()
    
    if result:
        print("\nПрограмма успешно завершила работу.")
    else:
        print("\nПрограмма завершилась с ошибкой.")
    
    print("\nРежим отладки завершен.")
    sleep(3) 
