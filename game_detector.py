import cv2
import numpy as np
import pyautogui
import time
import logging
import os
from PIL import Image, ImageDraw, ImageFont, ImageGrab
import threading
import logging
import json
import msvcrt  # Для обработки нажатий клавиш в Windows

# Попытка импорта win32 модулей с обработкой исключений
try:
    import win32gui
    import win32con
    import win32ui
    import win32process
    import ctypes
    import pywintypes
    PYWIN32_AVAILABLE = True
except ImportError:
    logging.warning("Не удалось импортировать модули pywin32. Будет использована упрощенная версия.")
    PYWIN32_AVAILABLE = False

# Импорт оповещений - при ошибках будет использоваться заглушка
try:
    from notification import GameNotification
except ImportError:
    logging.error("Ошибка импорта модуля notification. Использую встроенную заглушку.")
    
    # Встроенная заглушка для уведомлений
    class GameNotification:
        def __init__(self, title="GameDetector", position='top-right', duration=3.0, sound=False):
            self.title = title
            self.is_showing = False
            logging.info(f"Инициализирован встроенный класс уведомлений. Заголовок: {title}")
        
        def show(self, message, bg_color="#3366FF", fg_color="white"):
            print(f"\n[{self.title}] {message}")
            self.is_showing = True
        
        def close(self):
            if self.is_showing:
                self.is_showing = False

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='game_detector.log',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Путь к исполняемому файлу Tesseract OCR (если используется)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class GameDetector:
    def __init__(self):
        """Инициализация детектора"""
        # Настройка окна и региона
        self.window_title = "BlueStacks"
        self.window_handle = None  # Хендл окна
        self.window_rect = None    # Координаты окна (x1, y1, x2, y2)
        self.game_region = None    # Регион для поиска (x, y, width, height)
        
        # Список доступных окон
        self.available_windows = []
        self.current_window_index = 0
        self.show_window_list = False
        self.window_list_last_update = 0
        
        # Загрузка конфигурации цветов
        self.load_color_config()
        
        # Флаги состояния
        self.running = True
        self.notification = GameNotification(title="GameDetector")
        
        # Настройка экземпляра для выбора цветов
        self.color_picker = None
        
        # Цветовые диапазоны для определения объектов
        # Персонаж (фиолетовый)
        self.player_color_lower = np.array([140, 50, 50])
        self.player_color_upper = np.array([170, 255, 255])
        
        # Цель (зеленый)
        self.target_color_lower = np.array([40, 50, 50])
        self.target_color_upper = np.array([80, 255, 255])
        
        # Ловушка (красный)
        self.trap_color_lower = np.array([0, 50, 50])
        self.trap_color_upper = np.array([10, 255, 255])
        
        # Сохраняем последнее известное положение персонажа и цели
        self.player_position = None
        self.target_position = None
        self.trap_areas = []
        
        # Для отслеживания столкновений
        self.is_in_trap = False
        
        # Время последнего уведомления для предотвращения спама
        self.last_notification_time = 0
        
        # Флаг для выполнения только при достижении цели
        self.target_reached = False
        
        # Флаг для отображения визуализации
        self.show_visualization = True
        
        # Флаг для отслеживания открытого окна визуализации
        self.vis_window_open = False

    def find_window(self):
        """Поиск окна эмулятора по заголовку"""
        self.window_handle = None
        self.window_rect = None
        
        # Обновляем список всех видимых окон
        self.available_windows = []
        
        # Проверяем доступность win32gui
        if not PYWIN32_AVAILABLE:
            logging.warning("Модуль win32gui недоступен, использую простое определение экрана")
            # Получаем размер экрана для ограничения области захвата
            screen_width, screen_height = pyautogui.size()
            # Устанавливаем небольшой регион в центре экрана, если не нашли окно
            center_x = screen_width // 2
            center_y = screen_height // 2
            width = min(800, screen_width)
            height = min(600, screen_height)
            self.game_region = (center_x - width//2, center_y - height//2, width, height)
            print(f"Модуль win32gui недоступен. Используется область экрана: {self.game_region}")
            print("Используйте опцию 'Настроить цвета' для поиска объектов в этой области.")
            return True
        
        try:
            def callback(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if window_title:  # Игнорируем окна без заголовка
                        try:
                            rect = win32gui.GetWindowRect(hwnd)
                            # Проверяем, что окно имеет ненулевые размеры
                            if rect[2] - rect[0] > 50 and rect[3] - rect[1] > 50:
                                ctx.append((hwnd, window_title))
                                # Если это окно соответствует искомому заголовку
                                if self.window_title.lower() in window_title.lower():
                                    logging.info(f"Найдено окно, соответствующее критерию '{self.window_title}': {window_title} (handle: {hwnd})")
                        except:
                            pass  # Игнорируем окна, которые вызывают ошибки
                return True  # Продолжаем перебор окон
            
            # Получаем список всех окон
            win32gui.EnumWindows(callback, self.available_windows)
            
            # Если список окон не пуст, сортируем их по длине заголовка (для удобства просмотра)
            if self.available_windows:
                self.available_windows.sort(key=lambda x: len(x[1]))
                
                # Ищем окно, соответствующее критерию
                for i, (hwnd, title) in enumerate(self.available_windows):
                    if self.window_title.lower() in title.lower():
                        self.window_handle = hwnd
                        self.current_window_index = i
                        break
                
                # Если точного совпадения нет, берем первое
                if not self.window_handle and self.available_windows:
                    self.window_handle = self.available_windows[0][0]
                    self.current_window_index = 0
                    
                if self.window_handle:
                    self.window_rect = win32gui.GetWindowRect(self.window_handle)
                    logging.info(f"Выбрано окно: {win32gui.GetWindowText(self.window_handle)} (handle: {self.window_handle})")
            
        except Exception as e:
            logging.error(f"Ошибка при поиске окна: {e}")
            print(f"\nОШИБКА: Не удалось найти окно эмулятора ({e})")
            print(f"Убедитесь, что окно с названием '{self.window_title}' запущено перед запуском программы.")
            print("Если окно запущено, возможно, проблема с библиотекой pywin32.")
            print("Используйте опцию 'Установить заглушку для notification.py' в меню диагностики.")
            
            # Получаем размер экрана для ограничения области захвата
            screen_width, screen_height = pyautogui.size()
            # Устанавливаем небольшой регион в центре экрана, если не нашли окно
            center_x = screen_width // 2
            center_y = screen_height // 2
            width = min(800, screen_width)
            height = min(600, screen_height)
            self.game_region = (center_x - width//2, center_y - height//2, width, height)
            print(f"Используется область экрана: {self.game_region}")
            print("Используйте опцию 'Настроить цвета' для поиска объектов в этой области.")
            return True
        
        if self.window_handle and self.window_rect:
            print(f"Найдено окно: {win32gui.GetWindowText(self.window_handle)}")
            print(f"Размер окна: {self.window_rect}")
            # Устанавливаем game_region на основе window_rect
            self.game_region = (
                self.window_rect[0],  # x
                self.window_rect[1],  # y
                self.window_rect[2] - self.window_rect[0],  # width
                self.window_rect[3] - self.window_rect[1]   # height
            )
            return True
        else:
            print(f"\nОкно с названием '{self.window_title}' не найдено!")
            print("Убедитесь, что окно игры или эмулятора запущено и видно на экране.")
            print(f"Если вы используете другой эмулятор, измените название окна через настройки.")
            
            # Получаем размер экрана для ограничения области захвата
            screen_width, screen_height = pyautogui.size()
            # Устанавливаем небольшой регион в центре экрана, если не нашли окно
            center_x = screen_width // 2
            center_y = screen_height // 2
            width = min(800, screen_width)
            height = min(600, screen_height)
            self.game_region = (center_x - width//2, center_y - height//2, width, height)
            print(f"Используется ограниченная область экрана: {self.game_region}")
            print("Используйте опцию 'Настроить цвета' для поиска объектов в этой области.")
            return True

    def capture_screen(self):
        """Захват экрана в области окна игры"""
        try:
            if not self.game_region:
                logging.error("Не удалось захватить экран: регион не определен")
                return None
            
            # Захват области экрана
            screenshot = pyautogui.screenshot(region=self.game_region)
            return np.array(screenshot)
        except Exception as e:
            logging.error(f"Ошибка при захвате экрана: {e}")
            print(f"Ошибка при захвате экрана: {e}")
            return None
    
    def detect_objects(self, frame):
        """Обнаружить персонажа, цель и ловушки на кадре"""
        if frame is None:
            return None
        
        # Создаем копию кадра для визуализации
        visualization = frame.copy()
        
        # Конвертируем изображение в HSV для лучшего выделения цветов
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Обнаружение персонажа (фиолетовый цвет)
        player_mask = cv2.inRange(hsv, self.player_color_lower, self.player_color_upper)
        player_contours, _ = cv2.findContours(player_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Обнаружение цели (зеленый цвет)
        target_mask = cv2.inRange(hsv, self.target_color_lower, self.target_color_upper)
        target_contours, _ = cv2.findContours(target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Обнаружение ловушек (красный цвет)
        trap_mask = cv2.inRange(hsv, self.trap_color_lower, self.trap_color_upper)
        trap_contours, _ = cv2.findContours(trap_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Обработка персонажа
        if player_contours:
            # Находим самый большой контур (предполагаем, что это персонаж)
            player_contour = max(player_contours, key=cv2.contourArea)
            player_area = cv2.contourArea(player_contour)
            
            if player_area > 100:  # Минимальная площадь для обнаружения
                x, y, w, h = cv2.boundingRect(player_contour)
                self.player_position = (x + w//2, y + h//2)  # Центр персонажа
                cv2.rectangle(visualization, (x, y), (x + w, y + h), (255, 0, 255), 2)
                cv2.putText(visualization, "Player", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                logging.info(f"Персонаж обнаружен на позиции: {self.player_position}")
            
        # Обработка цели
        if target_contours:
            # Находим самый большой контур (предполагаем, что это цель)
            target_contour = max(target_contours, key=cv2.contourArea)
            target_area = cv2.contourArea(target_contour)
            
            if target_area > 100:  # Минимальная площадь для обнаружения
                x, y, w, h = cv2.boundingRect(target_contour)
                self.target_position = (x + w//2, y + h//2)  # Центр цели
                cv2.rectangle(visualization, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(visualization, "Target", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                logging.info(f"Цель обнаружена на позиции: {self.target_position}")
                
                # Проверка достижения цели
                self.check_target_reached()
        
        # Обработка ловушек
        self.trap_areas = []
        for contour in trap_contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Минимальная площадь для обнаружения
                x, y, w, h = cv2.boundingRect(contour)
                self.trap_areas.append((x, y, w, h))
                cv2.rectangle(visualization, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(visualization, "Trap", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        if self.trap_areas:
            logging.info(f"Обнаружено ловушек: {len(self.trap_areas)}")
        
        # Проверяем, находится ли персонаж в ловушке
        self.check_trap_collision()
        
        # Добавим дополнительную информацию на экран
        info_text = f"Игрок: {self.player_position}, Цель: {self.target_position}, Ловушек: {len(self.trap_areas)}"
        cv2.putText(visualization, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        if self.is_in_trap:
            warning_text = "ВНИМАНИЕ: ИГРОК В ЛОВУШКЕ!"
            cv2.putText(visualization, warning_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        if self.target_reached:
            success_text = "ЦЕЛЬ ДОСТИГНУТА!"
            cv2.putText(visualization, success_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Отобразить текущее окно
        window_title = f"Окно: {self.window_title}"
        cv2.putText(visualization, window_title, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Отобразить маски и контуры если нужна дополнительная отладка
        if self.show_visualization:
            # Создадим объединенное изображение масок для отображения
            combined_mask = cv2.merge([trap_mask, target_mask, player_mask])
            
            # Изменим размер для лучшего отображения
            vis_height, vis_width = visualization.shape[:2]
            mask_resized = cv2.resize(combined_mask, (vis_width // 3, vis_height // 3))
            
            # Вставим маску в правый нижний угол основного изображения
            roi = visualization[vis_height - mask_resized.shape[0]:vis_height, 
                                vis_width - mask_resized.shape[1]:vis_width]
            
            # Наложение масок в углу (опционально)
            # visualization[vis_height - mask_resized.shape[0]:vis_height, 
            #               vis_width - mask_resized.shape[1]:vis_width] = mask_resized
            
            # Добавим подсказки по управлению
            controls_text = "ESC: выход | V: вкл/выкл визуализацию | C: калибровка | S: сохранить"
            cv2.putText(visualization, controls_text, (10, vis_height - 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Добавляем подсказку о переключении окон
            window_controls_text = "W: следующее окно | Q: предыдущее окно | L: список окон"
            cv2.putText(visualization, window_controls_text, (10, vis_height - 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Если включен режим отображения списка окон
            if self.show_window_list:
                # Создаем полупрозрачный фон для списка окон
                overlay = visualization.copy()
                cv2.rectangle(overlay, (0, 0), (400, len(self.available_windows) * 20 + 40), (0, 0, 0), -1)
                alpha = 0.7  # Прозрачность
                cv2.addWeighted(overlay, alpha, visualization, 1 - alpha, 0, visualization)
                
                # Заголовок списка
                cv2.putText(visualization, "Доступные окна (Q/W для выбора):", (10, 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Выводим список окон
                for i, (_, title) in enumerate(self.available_windows):
                    # Укорачиваем слишком длинные заголовки
                    display_title = title[:40] + "..." if len(title) > 40 else title
                    color = (0, 255, 0) if i == self.current_window_index else (200, 200, 200)
                    cv2.putText(visualization, f"{i+1}. {display_title}", (10, 40 + i * 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        return visualization
    
    def check_trap_collision(self):
        """Проверить, находится ли персонаж в ловушке"""
        if not self.player_position:
            return
        
        player_x, player_y = self.player_position
        was_in_trap = self.is_in_trap
        self.is_in_trap = False
        
        for trap_x, trap_y, trap_w, trap_h in self.trap_areas:
            if (trap_x <= player_x <= trap_x + trap_w and 
                trap_y <= player_y <= trap_y + trap_h):
                self.is_in_trap = True
                if not was_in_trap:  # Чтобы выводить сообщение только при входе в ловушку
                    logging.warning("ИГРА ОКОНЧЕНА: Персонаж попал в ловушку!")
                    
                    # Проверяем, не слишком ли часто отправляем уведомления
                    current_time = time.time()
                    if current_time - self.last_notification_time > 5.0:  # Минимум 5 секунд между уведомлениями
                        self.notification.show("ИГРА ОКОНЧЕНА!\nВы попали в ловушку!")
                        self.last_notification_time = current_time
                break
        
        if was_in_trap and not self.is_in_trap:
            logging.info("Персонаж вышел из ловушки.")

    def check_target_reached(self):
        """Проверить, достиг ли персонаж цели"""
        if not self.player_position or not self.target_position:
            return
        
        player_x, player_y = self.player_position
        target_x, target_y = self.target_position
        
        # Вычисляем расстояние между персонажем и целью
        distance = np.sqrt((player_x - target_x)**2 + (player_y - target_y)**2)
        
        # Определяем, достаточно ли близко персонаж к цели
        if distance < 50 and not self.target_reached:  # Радиус 50 пикселей
            logging.info("Персонаж достиг цели!")
            self.target_reached = True
            
            # Показываем уведомление о достижении цели
            current_time = time.time()
            if current_time - self.last_notification_time > 5.0:
                self.notification.show("Поздравляем!\nВы достигли цели!", bg_color="#33CC33", fg_color="black")
                self.last_notification_time = current_time
        elif distance >= 50 and self.target_reached:
            # Сбрасываем флаг, если персонаж отошел от цели
            self.target_reached = False
    
    def calibrate_colors(self):
        """Открыть окно для калибровки цветов объектов"""
        def on_trackbar_change(val):
            # Обновляем HSV значения при изменении трекбара
            self.player_color_lower[0] = cv2.getTrackbarPos('P Hue Min', 'Calibration')
            self.player_color_upper[0] = cv2.getTrackbarPos('P Hue Max', 'Calibration')
            self.player_color_lower[1] = cv2.getTrackbarPos('P Sat Min', 'Calibration')
            self.player_color_upper[1] = cv2.getTrackbarPos('P Sat Max', 'Calibration')
            self.player_color_lower[2] = cv2.getTrackbarPos('P Val Min', 'Calibration')
            self.player_color_upper[2] = cv2.getTrackbarPos('P Val Max', 'Calibration')
            
            self.target_color_lower[0] = cv2.getTrackbarPos('T Hue Min', 'Calibration')
            self.target_color_upper[0] = cv2.getTrackbarPos('T Hue Max', 'Calibration')
            self.target_color_lower[1] = cv2.getTrackbarPos('T Sat Min', 'Calibration')
            self.target_color_upper[1] = cv2.getTrackbarPos('T Sat Max', 'Calibration')
            self.target_color_lower[2] = cv2.getTrackbarPos('T Val Min', 'Calibration')
            self.target_color_upper[2] = cv2.getTrackbarPos('T Val Max', 'Calibration')
            
            self.trap_color_lower[0] = cv2.getTrackbarPos('R Hue Min', 'Calibration')
            self.trap_color_upper[0] = cv2.getTrackbarPos('R Hue Max', 'Calibration')
            self.trap_color_lower[1] = cv2.getTrackbarPos('R Sat Min', 'Calibration')
            self.trap_color_upper[1] = cv2.getTrackbarPos('R Sat Max', 'Calibration')
            self.trap_color_lower[2] = cv2.getTrackbarPos('R Val Min', 'Calibration')
            self.trap_color_upper[2] = cv2.getTrackbarPos('R Val Max', 'Calibration')
        
        cv2.namedWindow('Calibration')
        
        # Создаем трекбары для настройки границ HSV
        # Для персонажа (фиолетовый)
        cv2.createTrackbar('P Hue Min', 'Calibration', int(self.player_color_lower[0]), 179, on_trackbar_change)
        cv2.createTrackbar('P Hue Max', 'Calibration', int(self.player_color_upper[0]), 179, on_trackbar_change)
        cv2.createTrackbar('P Sat Min', 'Calibration', int(self.player_color_lower[1]), 255, on_trackbar_change)
        cv2.createTrackbar('P Sat Max', 'Calibration', int(self.player_color_upper[1]), 255, on_trackbar_change)
        cv2.createTrackbar('P Val Min', 'Calibration', int(self.player_color_lower[2]), 255, on_trackbar_change)
        cv2.createTrackbar('P Val Max', 'Calibration', int(self.player_color_upper[2]), 255, on_trackbar_change)
        
        # Для цели (зеленый)
        cv2.createTrackbar('T Hue Min', 'Calibration', int(self.target_color_lower[0]), 179, on_trackbar_change)
        cv2.createTrackbar('T Hue Max', 'Calibration', int(self.target_color_upper[0]), 179, on_trackbar_change)
        cv2.createTrackbar('T Sat Min', 'Calibration', int(self.target_color_lower[1]), 255, on_trackbar_change)
        cv2.createTrackbar('T Sat Max', 'Calibration', int(self.target_color_upper[1]), 255, on_trackbar_change)
        cv2.createTrackbar('T Val Min', 'Calibration', int(self.target_color_lower[2]), 255, on_trackbar_change)
        cv2.createTrackbar('T Val Max', 'Calibration', int(self.target_color_upper[2]), 255, on_trackbar_change)
        
        # Для ловушек (красный)
        cv2.createTrackbar('R Hue Min', 'Calibration', int(self.trap_color_lower[0]), 179, on_trackbar_change)
        cv2.createTrackbar('R Hue Max', 'Calibration', int(self.trap_color_upper[0]), 179, on_trackbar_change)
        cv2.createTrackbar('R Sat Min', 'Calibration', int(self.trap_color_lower[1]), 255, on_trackbar_change)
        cv2.createTrackbar('R Sat Max', 'Calibration', int(self.trap_color_upper[1]), 255, on_trackbar_change)
        cv2.createTrackbar('R Val Min', 'Calibration', int(self.trap_color_lower[2]), 255, on_trackbar_change)
        cv2.createTrackbar('R Val Max', 'Calibration', int(self.trap_color_upper[2]), 255, on_trackbar_change)
        
        while True:
            new_frame = self.capture_screen()
            if new_frame is None:
                break
                
            # Конвертируем в HSV
            hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV)
            
            # Создаем маски для всех объектов
            player_mask = cv2.inRange(hsv, self.player_color_lower, self.player_color_upper)
            target_mask = cv2.inRange(hsv, self.target_color_lower, self.target_color_upper)
            trap_mask = cv2.inRange(hsv, self.trap_color_lower, self.trap_color_upper)
            
            # Объединяем маски
            result = cv2.bitwise_and(new_frame, new_frame, mask=player_mask + target_mask + trap_mask)
            
            # Отображаем оригинальное и отфильтрованное изображения
            cv2.imshow('Original', new_frame)
            cv2.imshow('Filtered', result)
            
            # Выход по нажатию клавиши ESC
            key = cv2.waitKey(1)
            if key == 27:  # ESC
                break
        
        cv2.destroyAllWindows()
        logging.info("Калибровка завершена")
        
        # Вывести текущие настройки цветов
        logging.info(f"Персонаж HSV: {self.player_color_lower} - {self.player_color_upper}")
        logging.info(f"Цель HSV: {self.target_color_lower} - {self.target_color_upper}")
        logging.info(f"Ловушка HSV: {self.trap_color_lower} - {self.trap_color_upper}")
        
        return True
    
    def save_config(self, filename="color_config.json"):
        """Сохранить настройки цветов в JSON файл"""
        config = {
            "player_color_lower": self.player_color_lower.tolist(),
            "player_color_upper": self.player_color_upper.tolist(),
            "target_color_lower": self.target_color_lower.tolist(),
            "target_color_upper": self.target_color_upper.tolist(),
            "trap_color_lower": self.trap_color_lower.tolist(),
            "trap_color_upper": self.trap_color_upper.tolist()
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=4)
            logging.info(f"Конфигурация сохранена в {filename}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении конфигурации: {e}")
            return False
    
    def load_config(self, filename="color_config.json"):
        """Загрузить настройки цветов из JSON файла"""
        try:
            with open(filename, 'r') as f:
                config = json.load(f)
                
            self.player_color_lower = np.array(config["player_color_lower"])
            self.player_color_upper = np.array(config["player_color_upper"])
            self.target_color_lower = np.array(config["target_color_lower"])
            self.target_color_upper = np.array(config["target_color_upper"])
            self.trap_color_lower = np.array(config["trap_color_lower"])
            self.trap_color_upper = np.array(config["trap_color_upper"])
            
            logging.info(f"Конфигурация загружена из {filename}")
            return True
        except FileNotFoundError:
            logging.warning(f"Файл конфигурации {filename} не найден. Используются значения по умолчанию.")
            return False
        except Exception as e:
            logging.error(f"Ошибка при загрузке конфигурации: {e}")
            return False
    
    def run(self):
        """Основной цикл программы"""
        if not self.find_window():
            print(f"Не удалось найти окно игры. Убедитесь, что окно с названием '{self.window_title}' запущено.")
            return

        print(f"Поиск объектов запущен. Окно игры: {self.window_title}")
        print("Управление программой:")
        print("- ESC: выход из программы")
        print("- V: включить/выключить визуализацию")
        print("- C: калибровка цветов")
        print("- S: сохранение настроек")
        print("- P: запуск инструмента выбора цветов")
        print("- W: переключиться на следующее окно")
        print("- Q: переключиться на предыдущее окно")
        print("- L: показать список доступных окон")
        
        # Установка флага запуска
        self.running = True
        
        # Создаем окно для отображения визуализации
        if self.show_visualization:
            try:
                cv2.namedWindow("GameDetector - Визуализация", cv2.WINDOW_NORMAL)
                cv2.resizeWindow("GameDetector - Визуализация", 800, 600)
                self.vis_window_open = True
                
                # Добавляем обработчик закрытия окна
                def on_close(event, x, y, flags, param):
                    if event == cv2.EVENT_LBUTTONDOWN:
                        pass  # просто заглушка для обработчика событий
                cv2.setMouseCallback("GameDetector - Визуализация", on_close)
            except Exception as e:
                logging.error(f"Не удалось создать окно визуализации: {e}")
                self.show_visualization = False
                self.vis_window_open = False
        
        # Счетчик для проверки window_handle
        window_check_counter = 0
        
        # Главный цикл
        while self.running:
            try:
                # Периодически проверяем, существует ли еще окно
                window_check_counter += 1
                if window_check_counter >= 50:  # Каждые ~5 секунд
                    window_check_counter = 0
                    if PYWIN32_AVAILABLE and self.window_handle:
                        try:
                            # Проверяем, существует ли еще окно
                            if not win32gui.IsWindow(self.window_handle):
                                logging.info("Окно больше не существует, ищем его снова")
                                self.find_window()
                        except:
                            self.find_window()
                
                # Захват экрана
                screen = self.capture_screen()
                if screen is None:
                    print("Не удалось захватить экран. Повторная попытка...")
                    time.sleep(1)
                    continue
                
                # Анализ экрана и поиск объектов
                visualization = self.detect_objects(screen)
                
                # Отображаем визуализацию, если включена
                if self.show_visualization and visualization is not None:
                    try:
                        # Проверяем, существует ли окно визуализации
                        if not self.vis_window_open:
                            cv2.namedWindow("GameDetector - Визуализация", cv2.WINDOW_NORMAL)
                            cv2.resizeWindow("GameDetector - Визуализация", 800, 600)
                            self.vis_window_open = True
                            
                        cv2.imshow("GameDetector - Визуализация", visualization)
                        key_pressed = cv2.waitKey(1)  # Необходимо для обновления окна OpenCV
                        
                        # Проверяем, было ли окно закрыто пользователем
                        try:
                            if cv2.getWindowProperty("GameDetector - Визуализация", cv2.WND_PROP_VISIBLE) < 1:
                                print("Окно визуализации было закрыто. Выключаем визуализацию.")
                                self.vis_window_open = False
                        except:
                            self.vis_window_open = False
                        
                        # Обработка клавиш через OpenCV
                        if key_pressed == 27:  # ESC
                            self.running = False
                            print("ESC нажат. Выход из программы.")
                        elif key_pressed == ord('v'):
                            self.show_visualization = not self.show_visualization
                            print(f"Визуализация {'включена' if self.show_visualization else 'выключена'}")
                        elif key_pressed == ord('c'):
                            self.calibrate_colors()
                        elif key_pressed == ord('s'):
                            self.save_config()
                            self.notification.show("Настройки сохранены!", bg_color="#3366FF", fg_color="white")
                        elif key_pressed == ord('p'):
                            self.run_color_picker()
                        elif key_pressed == ord('w'):  # Следующее окно
                            self.switch_window(next_window=True)
                        elif key_pressed == ord('q'):  # Предыдущее окно
                            self.switch_window(next_window=False)
                        elif key_pressed == ord('l'):  # Показать/скрыть список окон
                            self.show_window_list = not self.show_window_list
                            print(f"Список окон {'показан' if self.show_window_list else 'скрыт'}")
                    except cv2.error as e:
                        # Если окно было закрыто, отключаем визуализацию
                        logging.error(f"Ошибка OpenCV: {e}. Выключаем визуализацию.")
                        self.vis_window_open = False
                
                # Проверка нажатия клавиш (без использования модуля keyboard)
                if msvcrt.kbhit():  # Проверяем, была ли нажата клавиша
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == '\x1b':  # ESC
                        self.running = False
                        print("ESC нажат. Выход из программы.")
                    elif key == 'c':
                        self.calibrate_colors()
                    elif key == 's':
                        self.save_config()
                        self.notification.show("Настройки сохранены!", bg_color="#3366FF", fg_color="white")
                    elif key == 'p':
                        self.run_color_picker()
                    elif key == 'v':
                        self.show_visualization = not self.show_visualization
                        if self.show_visualization and not self.vis_window_open:
                            print("Визуализация включена")
                            try:
                                cv2.namedWindow("GameDetector - Визуализация", cv2.WINDOW_NORMAL)
                                cv2.resizeWindow("GameDetector - Визуализация", 800, 600)
                                self.vis_window_open = True
                            except Exception as e:
                                logging.error(f"Не удалось создать окно визуализации: {e}")
                                print(f"Не удалось создать окно визуализации: {e}")
                        elif not self.show_visualization:
                            print("Визуализация выключена")
                            try:
                                cv2.destroyWindow("GameDetector - Визуализация")
                                self.vis_window_open = False
                            except:
                                pass  # Окно уже может быть закрыто
                    elif key == 'w':  # Следующее окно
                        self.switch_window(next_window=True)
                    elif key == 'q':  # Предыдущее окно
                        self.switch_window(next_window=False)
                    elif key == 'l':  # Показать/скрыть список окон
                        self.show_window_list = not self.show_window_list
                        print(f"Список окон {'показан' if self.show_window_list else 'скрыт'}")
                
                # Небольшая пауза для снижения нагрузки на CPU
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Ошибка в главном цикле: {e}")
                print(f"Ошибка: {e}")
                time.sleep(1)
        
        # Закрываем все окна OpenCV перед выходом
        try:
            cv2.destroyAllWindows()
            self.vis_window_open = False
        except:
            pass
        print("Программа завершена.")

    def load_color_config(self):
        """Загрузка настроек цветовых диапазонов из JSON-файла"""
        config_file = "color_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                # Загрузка цветовых диапазонов
                self.player_color_lower = np.array(config.get("player_color_lower", self.player_color_lower))
                self.player_color_upper = np.array(config.get("player_color_upper", self.player_color_upper))
                self.target_color_lower = np.array(config.get("target_color_lower", self.target_color_lower))
                self.target_color_upper = np.array(config.get("target_color_upper", self.target_color_upper))
                self.trap_color_lower = np.array(config.get("trap_color_lower", self.trap_color_lower))
                self.trap_color_upper = np.array(config.get("trap_color_upper", self.trap_color_upper))
                logging.info(f"Конфигурация загружена из {config_file}")
            else:
                logging.warning(f"Файл конфигурации {config_file} не найден. Используются значения по умолчанию.")
        except Exception as e:
            logging.error(f"Ошибка при загрузке конфигурации: {e}")
            print(f"Ошибка при загрузке конфигурации: {e}")

    def save_color_config(self):
        """Сохранение настроек цветовых диапазонов в JSON-файл"""
        config_file = "color_config.json"
        try:
            config = {
                "player_color_lower": self.player_color_lower.tolist(),
                "player_color_upper": self.player_color_upper.tolist(),
                "target_color_lower": self.target_color_lower.tolist(),
                "target_color_upper": self.target_color_upper.tolist(),
                "trap_color_lower": self.trap_color_lower.tolist(),
                "trap_color_upper": self.trap_color_upper.tolist()
            }
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            logging.info(f"Конфигурация сохранена в {config_file}")
            print(f"Настройки сохранены в {config_file}")
            return True
        except Exception as e:
            logging.error(f"Ошибка при сохранении конфигурации: {e}")
            print(f"Ошибка при сохранении конфигурации: {e}")
            return False

    def run_color_picker(self):
        """Запуск инструмента выбора цветов"""
        try:
            print("Запуск инструмента выбора цветов...")
            if os.path.exists("color_picker.py"):
                # Сохраняем текущее состояние
                self.running = False
                
                # Запуск инструмента в отдельном процессе
                import subprocess
                subprocess.run(["py", "color_picker.py"], check=True)
                
                # Перезагружаем конфигурацию
                self.load_color_config()
                
                # Возобновляем работу
                self.running = True
                print("Инструмент выбора цветов завершил работу, конфигурация перезагружена")
            else:
                print("ОШИБКА: Файл color_picker.py не найден!")
        except Exception as e:
            logging.error(f"Ошибка при запуске инструмента выбора цветов: {e}")
            print(f"Ошибка при запуске выбора цветов: {e}")

    def check_overlap(self, box1, box2):
        """Проверка перекрытия двух прямоугольников"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2
        
        # Вычисляем координаты углов прямоугольников
        left1, right1 = x1, x1 + w1
        top1, bottom1 = y1, y1 + h1
        
        left2, right2 = x2, x2 + w2
        top2, bottom2 = y2, y2 + h2
        
        # Проверяем перекрытие
        return not (right1 < left2 or left1 > right2 or bottom1 < top2 or top1 > bottom2)

    def send_notification(self, message, color="blue"):
        """Отправить уведомление с учетом задержки"""
        current_time = time.time()
        if current_time - self.last_notification_time >= 3.0:  # Минимальный интервал между уведомлениями
            if color == "red":
                bg_color = "#FF3333"
            elif color == "green":
                bg_color = "#33CC33"
            else:
                bg_color = "#3366FF"
            
            self.notification.show(message, bg_color=bg_color, fg_color="white")
            self.last_notification_time = current_time
            logging.info(f"Отправлено уведомление: {message}")

    def switch_window(self, next_window=True):
        """Переключение на следующее или предыдущее окно в списке доступных окон"""
        if not self.available_windows:
            print("Нет доступных окон для переключения")
            return False
        
        # Обновляем список доступных окон не чаще, чем раз в 10 секунд
        current_time = time.time()
        if current_time - self.window_list_last_update > 10:
            self.find_window()  # Это обновит self.available_windows
            self.window_list_last_update = current_time
        
        # Вычисляем новый индекс
        total_windows = len(self.available_windows)
        if next_window:
            self.current_window_index = (self.current_window_index + 1) % total_windows
        else:
            self.current_window_index = (self.current_window_index - 1) % total_windows
        
        # Устанавливаем новое окно
        hwnd, title = self.available_windows[self.current_window_index]
        self.window_handle = hwnd
        self.window_title = title  # Обновляем заголовок окна
        self.window_rect = win32gui.GetWindowRect(hwnd)
        
        # Обновляем game_region
        self.game_region = (
            self.window_rect[0],
            self.window_rect[1],
            self.window_rect[2] - self.window_rect[0],
            self.window_rect[3] - self.window_rect[1]
        )
        
        print(f"Переключено на окно: {title}")
        return True

if __name__ == "__main__":
    detector = GameDetector()
    detector.run() 