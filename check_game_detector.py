"""
Скрипт для проверки синтаксиса и содержимого файла game_detector.py
"""

import os
import sys
import re
import traceback

def check_file_existence():
    """Проверяет наличие файла game_detector.py"""
    print("\n=== Проверка наличия файла ===")
    if os.path.isfile("game_detector.py"):
        file_size = os.path.getsize("game_detector.py")
        print(f"Файл game_detector.py найден (размер: {file_size} байт)")
        return True
    else:
        print("ОШИБКА: Файл game_detector.py не найден!")
        return False

def check_file_encoding():
    """Проверяет кодировку файла"""
    print("\n=== Проверка кодировки файла ===")
    encodings = ['utf-8', 'cp1251', 'latin-1']
    
    for encoding in encodings:
        try:
            with open("game_detector.py", 'r', encoding=encoding) as f:
                content = f.read()
                print(f"Файл успешно открыт с кодировкой {encoding}")
                return content, encoding
        except UnicodeDecodeError:
            print(f"Не удалось открыть файл с кодировкой {encoding}")
    
    print("ОШИБКА: Не удалось определить кодировку файла!")
    return None, None

def check_syntax(content):
    """Проверяет синтаксис Python-кода"""
    print("\n=== Проверка синтаксиса Python ===")
    try:
        compile(content, "game_detector.py", "exec")
        print("Синтаксис кода корректен")
        return True
    except SyntaxError as e:
        print(f"ОШИБКА СИНТАКСИСА: {str(e)}")
        line_number = e.lineno
        if line_number and content:
            lines = content.splitlines()
            if 1 <= line_number <= len(lines):
                print(f"Строка {line_number}: {lines[line_number-1]}")
                if line_number > 1:
                    print(f"Строка {line_number-1}: {lines[line_number-2]}")
                if line_number < len(lines):
                    print(f"Строка {line_number+1}: {lines[line_number]}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка при проверке синтаксиса: {str(e)}")
        traceback.print_exc()
        return False

def check_imports(content):
    """Анализирует импорты в файле"""
    print("\n=== Анализ импортов ===")
    import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+([^,\s]+))'
    imports = []
    
    for line in content.splitlines():
        match = re.match(import_pattern, line.strip())
        if match:
            module = match.group(1) or match.group(2)
            imports.append(module)
    
    print(f"Найдено {len(imports)} импортов:")
    for module in imports:
        try:
            # Проверка доступности модуля
            __import__(module.split('.')[0])
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - ОШИБКА: {str(e)}")
    
    return imports

def check_class_definition(content):
    """Проверяет определение класса GameDetector"""
    print("\n=== Проверка определения класса ===")
    if "class GameDetector" in content:
        print("Класс GameDetector найден в файле")
        # Проверка наличия метода run
        if "def run(self" in content:
            print("Метод run() найден в классе")
        else:
            print("ВНИМАНИЕ: Метод run() не найден в классе!")
        return True
    else:
        print("ОШИБКА: Класс GameDetector не найден в файле!")
        return False

def check_main_block(content):
    """Проверяет наличие блока if __name__ == "__main__" """
    print("\n=== Проверка блока main ===")
    if '__name__ == "__main__"' in content or "__name__ == '__main__'" in content:
        print("Блок if __name__ == \"__main__\" найден")
        return True
    else:
        print("ВНИМАНИЕ: Блок if __name__ == \"__main__\" не найден!")
        return False

def repair_known_issues(content, encoding):
    """Пытается исправить известные проблемы в коде"""
    print("\n=== Попытка исправить известные проблемы ===")
    
    # Проверка на ошибки импорта notification
    if "from notification import GameNotification" in content:
        print("Проверка импорта notification...")
        if not os.path.isfile("notification.py"):
            print("ПРОБЛЕМА: Файл notification.py не найден!")
            print("Создаю временную заглушку для notification.py...")
            
            with open("notification.py.temp", "w", encoding="utf-8") as f:
                f.write('''
class GameNotification:
    """Заглушка для класса GameNotification"""
    def __init__(self, title="", position='', duration=0, sound=False):
        self.title = title
        print(f"[STUB] GameNotification.__init__({title})")
    
    def show(self, message, bg_color="", fg_color=""):
        print(f"[STUB] GameNotification.show({message})")
    
    def close(self):
        print("[STUB] GameNotification.close()")
''')
            
            print("Заглушка создана как notification.py.temp")
            print("Вы можете переименовать ее в notification.py, если хотите использовать")
    
    # Возможные исправления можно добавить здесь
    
    return content

def main():
    print("=== Проверка файла game_detector.py ===")
    
    # 1. Проверка наличия файла
    if not check_file_existence():
        return
    
    # 2. Проверка кодировки и чтение содержимого
    content, encoding = check_file_encoding()
    if not content:
        return
    
    # 3. Проверка синтаксиса
    if not check_syntax(content):
        print("\nОБНАРУЖЕНЫ СИНТАКСИЧЕСКИЕ ОШИБКИ!")
        print("Исправьте их перед запуском программы.")
    
    # 4. Анализ импортов
    imports = check_imports(content)
    
    # 5. Проверка определения класса
    check_class_definition(content)
    
    # 6. Проверка блока main
    check_main_block(content)
    
    # 7. Попытка исправить известные проблемы
    repair_known_issues(content, encoding)
    
    print("\n=== Проверка завершена ===")
    print("Если вы видите ошибки выше, исправьте их и попробуйте снова запустить программу.")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main() 