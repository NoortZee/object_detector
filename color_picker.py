import cv2
import numpy as np
import pyautogui
import os
import json
import time

class ColorPicker:
    def __init__(self):
        print("Инициализация инструмента выбора цветов...")
        # Настройка окна и региона для захвата
        self.capture_width = 800
        self.capture_height = 600
        
        # Получаем размер экрана
        screen_width, screen_height = pyautogui.size()
        
        # Центрируем область захвата по центру экрана
        self.region = (
            screen_width // 2 - self.capture_width // 2,
            screen_height // 2 - self.capture_height // 2,
            self.capture_width,
            self.capture_height
        )
        
        # Текущие значения HSV для каждого объекта
        self.selected_hsv = None
        self.selected_type = None
        
        # Настройки цветов для объектов
        self.player_color_range = {
            "lower": [140, 50, 50],
            "upper": [170, 255, 255]
        }
        
        self.target_color_range = {
            "lower": [40, 50, 50],
            "upper": [80, 255, 255]
        }
        
        self.trap_color_range = {
            "lower": [0, 50, 50],
            "upper": [10, 255, 255]
        }
        
        # Загрузка существующих настроек, если они есть
        self.load_config()
        
        # Режим выбора (player, target, trap)
        self.selection_mode = "player"
        
        # Флаг для отслеживания, была ли изменена конфигурация
        self.config_changed = False
        
        # Координаты для отображения выбранного цвета
        self.color_rect_x = 10
        self.color_rect_y = 30
        self.color_rect_width = 50
        self.color_rect_height = 50
        
    def load_config(self, filename="color_config.json"):
        """Загрузить существующие настройки цветов"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                
                # Загружаем настройки для каждого объекта
                if "player_color_lower" in config and "player_color_upper" in config:
                    self.player_color_range["lower"] = config["player_color_lower"]
                    self.player_color_range["upper"] = config["player_color_upper"]
                
                if "target_color_lower" in config and "target_color_upper" in config:
                    self.target_color_range["lower"] = config["target_color_lower"]
                    self.target_color_range["upper"] = config["target_color_upper"]
                
                if "trap_color_lower" in config and "trap_color_upper" in config:
                    self.trap_color_range["lower"] = config["trap_color_lower"]
                    self.trap_color_range["upper"] = config["trap_color_upper"]
                
                print(f"Конфигурация загружена из {filename}")
                return True
            except Exception as e:
                print(f"Ошибка при загрузке конфигурации: {e}")
                return False
        else:
            print(f"Файл конфигурации {filename} не найден. Будут использованы значения по умолчанию.")
            return False
    
    def save_config(self, filename="color_config.json"):
        """Сохранить настройки цветов в файл"""
        config = {
            "player_color_lower": self.player_color_range["lower"],
            "player_color_upper": self.player_color_range["upper"],
            "target_color_lower": self.target_color_range["lower"],
            "target_color_upper": self.target_color_range["upper"],
            "trap_color_lower": self.trap_color_range["lower"],
            "trap_color_upper": self.trap_color_range["upper"]
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"Конфигурация сохранена в {filename}")
            self.config_changed = False
            return True
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
            return False
    
    def capture_screen(self):
        """Захват экрана в указанной области"""
        try:
            screenshot = pyautogui.screenshot(region=self.region)
            return np.array(screenshot)
        except Exception as e:
            print(f"Ошибка при захвате экрана: {e}")
            return None
    
    def click_event(self, event, x, y, flags, param):
        """Обработчик событий мыши"""
        if event == cv2.EVENT_LBUTTONDOWN:
            # Получаем изображение и цвет пикселя
            frame = self.capture_screen()
            if frame is not None:
                # Конвертируем в HSV
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                
                # Получаем HSV значение пикселя
                self.selected_hsv = hsv[y, x]
                self.selected_type = self.selection_mode
                
                # Обновляем диапазоны цветов для выбранного объекта
                h, s, v = self.selected_hsv
                
                # Для каждого типа объекта устанавливаем разные диапазоны вокруг выбранного цвета
                if self.selection_mode == "player":
                    # Для персонажа (фиолетовый диапазон)
                    h_range = 15  # допустимое отклонение оттенка
                    self.player_color_range["lower"] = [max(0, h - h_range), max(0, s - 50), max(0, v - 50)]
                    self.player_color_range["upper"] = [min(179, h + h_range), min(255, s + 50), min(255, v + 50)]
                    print(f"Выбран цвет для персонажа: HSV={self.selected_hsv}")
                
                elif self.selection_mode == "target":
                    # Для цели (зеленый диапазон)
                    h_range = 20
                    self.target_color_range["lower"] = [max(0, h - h_range), max(0, s - 50), max(0, v - 50)]
                    self.target_color_range["upper"] = [min(179, h + h_range), min(255, s + 50), min(255, v + 50)]
                    print(f"Выбран цвет для цели: HSV={self.selected_hsv}")
                
                elif self.selection_mode == "trap":
                    # Для ловушек (красный диапазон)
                    h_range = 10
                    self.trap_color_range["lower"] = [max(0, h - h_range), max(0, s - 50), max(0, v - 50)]
                    self.trap_color_range["upper"] = [min(179, h + h_range), min(255, s + 50), min(255, v + 50)]
                    print(f"Выбран цвет для ловушки: HSV={self.selected_hsv}")
                
                # Отмечаем, что конфигурация была изменена
                self.config_changed = True
    
    def run(self):
        """Основной цикл работы инструмента выбора цветов"""
        print("=== Инструмент выбора цветов ===")
        print(f"Область захвата экрана: {self.region}")
        print("\nКлавиши управления:")
        print("1 - выбор цвета персонажа (фиолетовый)")
        print("2 - выбор цвета цели (зеленый)")
        print("3 - выбор цвета ловушки (красный)")
        print("S - сохранить настройки")
        print("ESC - выход")
        print("\nЩелкните на нужном цвете на экране для его выбора.")
        
        # Создаем окно и устанавливаем обработчик событий мыши
        cv2.namedWindow("Color Picker")
        cv2.setMouseCallback("Color Picker", self.click_event)
        
        while True:
            # Захват экрана
            frame = self.capture_screen()
            if frame is None:
                print("Не удалось захватить экран")
                time.sleep(1)
                continue
            
            # Конвертируем в HSV для детекции цветов
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # Создаем маски для каждого объекта
            player_mask = cv2.inRange(
                hsv, 
                np.array(self.player_color_range["lower"]), 
                np.array(self.player_color_range["upper"])
            )
            
            target_mask = cv2.inRange(
                hsv, 
                np.array(self.target_color_range["lower"]), 
                np.array(self.target_color_range["upper"])
            )
            
            trap_mask = cv2.inRange(
                hsv, 
                np.array(self.trap_color_range["lower"]), 
                np.array(self.trap_color_range["upper"])
            )
            
            # Объединяем маски и исходное изображение
            result = frame.copy()
            
            # Накладываем маски разных цветов
            # Персонаж - фиолетовый
            player_result = cv2.bitwise_and(frame, frame, mask=player_mask)
            player_highlight = np.zeros_like(frame)
            player_highlight[player_mask > 0] = [255, 0, 255]  # Фиолетовый
            result = cv2.addWeighted(result, 1, player_highlight, 0.5, 0)
            
            # Цель - зеленый
            target_result = cv2.bitwise_and(frame, frame, mask=target_mask)
            target_highlight = np.zeros_like(frame)
            target_highlight[target_mask > 0] = [0, 255, 0]  # Зеленый
            result = cv2.addWeighted(result, 1, target_highlight, 0.5, 0)
            
            # Ловушки - красный
            trap_result = cv2.bitwise_and(frame, frame, mask=trap_mask)
            trap_highlight = np.zeros_like(frame)
            trap_highlight[trap_mask > 0] = [0, 0, 255]  # Красный
            result = cv2.addWeighted(result, 1, trap_highlight, 0.5, 0)
            
            # Отображаем текущий режим выбора
            mode_text = f"Режим: {self.selection_mode.upper()}"
            cv2.putText(result, mode_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Показываем прямоугольник с выбранным цветом
            if self.selected_hsv is not None and self.selected_type is not None:
                # Определяем цвет прямоугольника в зависимости от типа
                if self.selected_type == "player":
                    color = (255, 0, 255)  # Фиолетовый
                    ranges_text = f"Персонаж: H[{self.player_color_range['lower'][0]}-{self.player_color_range['upper'][0]}] S[{self.player_color_range['lower'][1]}-{self.player_color_range['upper'][1]}] V[{self.player_color_range['lower'][2]}-{self.player_color_range['upper'][2]}]"
                elif self.selected_type == "target":
                    color = (0, 255, 0)    # Зеленый
                    ranges_text = f"Цель: H[{self.target_color_range['lower'][0]}-{self.target_color_range['upper'][0]}] S[{self.target_color_range['lower'][1]}-{self.target_color_range['upper'][1]}] V[{self.target_color_range['lower'][2]}-{self.target_color_range['upper'][2]}]"
                elif self.selected_type == "trap":
                    color = (0, 0, 255)    # Красный
                    ranges_text = f"Ловушка: H[{self.trap_color_range['lower'][0]}-{self.trap_color_range['upper'][0]}] S[{self.trap_color_range['lower'][1]}-{self.trap_color_range['upper'][1]}] V[{self.trap_color_range['lower'][2]}-{self.trap_color_range['upper'][2]}]"
                
                # Рисуем прямоугольник с выбранным цветом
                cv2.rectangle(result, 
                              (self.color_rect_x, self.color_rect_y), 
                              (self.color_rect_x + self.color_rect_width, self.color_rect_y + self.color_rect_height), 
                              color, -1)
                
                # Выводим HSV значение выбранного цвета
                hsv_text = f"HSV: {self.selected_hsv}"
                cv2.putText(result, hsv_text, (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Выводим диапазоны для выбранного типа
                cv2.putText(result, ranges_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Отображаем инструкции
            cv2.putText(result, "1: персонаж  2: цель  3: ловушка", (10, result.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(result, "S: сохранить  ESC: выход", (10, result.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Показываем результат
            cv2.imshow("Color Picker", result)
            
            # Обработка нажатий клавиш
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC - выход
                if self.config_changed:
                    print("Конфигурация была изменена. Сохранить перед выходом? (y/n)")
                    save_key = cv2.waitKey(0) & 0xFF
                    if save_key == ord('y'):
                        self.save_config()
                break
            elif key == ord('1'):  # Выбор персонажа
                self.selection_mode = "player"
                print("Выбран режим настройки цвета персонажа")
            elif key == ord('2'):  # Выбор цели
                self.selection_mode = "target"
                print("Выбран режим настройки цвета цели")
            elif key == ord('3'):  # Выбор ловушки
                self.selection_mode = "trap"
                print("Выбран режим настройки цвета ловушки")
            elif key == ord('s'):  # Сохранение настроек
                self.save_config()
        
        # Закрываем окно
        cv2.destroyAllWindows()
        print("Инструмент выбора цветов завершил работу")

if __name__ == "__main__":
    picker = ColorPicker()
    picker.run() 