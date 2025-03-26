"""
Упрощенная версия модуля уведомлений, не использующая win32gui
"""

import logging
import time

class GameNotification:
    """Класс для отображения уведомлений в игре без использования GUI"""
    
    def __init__(self, title="GameDetector", position='top-right', duration=3.0, sound=False):
        """
        Инициализация уведомления
        
        Args:
            title (str): Заголовок уведомления
            position (str): Позиция уведомления ('top-right', 'top-left', 'bottom-right', 'bottom-left')
            duration (float): Длительность отображения в секундах
            sound (bool): Проигрывать ли звук при показе уведомления
        """
        self.title = title
        self.position = position
        self.duration = duration
        self.sound = sound
        self.is_showing = False
        logging.info(f"Инициализирован класс уведомлений. Заголовок: {title}")
    
    def show(self, message, bg_color="#3366FF", fg_color="white"):
        """
        Показать уведомление
        
        Args:
            message (str): Текст уведомления
            bg_color (str): Цвет фона (hex)
            fg_color (str): Цвет текста (hex)
        """
        # В этой упрощенной версии просто выводим сообщение в консоль
        print(f"\n[{self.title}] {message}")
        print(f"Цвета: фон={bg_color}, текст={fg_color}")
        
        self.is_showing = True
        logging.info(f"Показано уведомление: {message}")
        
        # Имитация автоматического закрытия уведомления
        if self.duration > 0:
            time.sleep(0.1)  # Очень короткая задержка
            self.close()
    
    def close(self):
        """Закрыть уведомление"""
        if self.is_showing:
            self.is_showing = False
            logging.info("Уведомление закрыто")

# Пример использования
if __name__ == "__main__":
    # Настройка логгера
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Создание и использование уведомления
    notification = GameNotification(title="Тестовое уведомление")
    notification.show("Это тестовое уведомление!")
    time.sleep(1)
    notification.show("Внимание! Ловушка!", bg_color="#FF3333")
    time.sleep(1)
    notification.show("Цель достигнута!", bg_color="#33CC33") 