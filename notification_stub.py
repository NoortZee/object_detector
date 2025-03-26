"""
Упрощенная версия модуля уведомлений без использования win32gui
Используйте эту версию, если у вас проблемы с pywin32
"""

import logging
import time
import os

class GameNotification:
    """
    Класс для отображения простых консольных уведомлений
    Заменяет GUI-версию при проблемах с библиотеками Windows
    """
    
    def __init__(self, title="GameDetector", position='top-right', duration=3.0, sound=False):
        """
        Инициализация уведомления
        
        Args:
            title (str): Заголовок уведомления
            position (str): Позиция уведомления (игнорируется в этой версии)
            duration (float): Длительность отображения в секундах
            sound (bool): Проигрывать ли звук при показе уведомления
        """
        self.title = title
        self.position = position
        self.duration = duration
        self.sound = sound
        self.is_showing = False
        logging.info(f"Инициализирован класс уведомлений (STUB). Заголовок: {title}")
    
    def show(self, message, bg_color="#3366FF", fg_color="white"):
        """
        Показать уведомление в консоли
        
        Args:
            message (str): Текст уведомления
            bg_color (str): Цвет фона (игнорируется в консольном режиме)
            fg_color (str): Цвет текста (игнорируется в консольном режиме)
        """
        os.system("cls" if os.name == "nt" else "clear")
        border = "=" * (len(self.title) + len(message) + 10)
        print("\n\n")
        print(border)
        print(f"| {self.title}: {message} |")
        print(border)
        print("\n")
        
        self.is_showing = True
        logging.info(f"Показано уведомление (STUB): {message}")
        
        # Имитация автоматического закрытия уведомления
        if self.duration > 0:
            time.sleep(0.5)  # Короткая задержка
            self.close()
    
    def close(self):
        """Закрыть уведомление (просто меняет флаг)"""
        if self.is_showing:
            self.is_showing = False
            logging.info("Уведомление (STUB) закрыто")


if __name__ == "__main__":
    # Пример использования
    print("Тестирование заглушки уведомлений...")
    notifier = GameNotification("Тест")
    notifier.show("Это тестовое уведомление")
    print("Тест завершен.") 