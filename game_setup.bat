@echo off
setlocal EnableDelayedExpansion
title GameDetector - Установка и запуск
color 0A

REM Добавляем небольшую задержку в начале для стабильности
ping -n 1 127.0.0.1 > nul

echo ===== GameDetector - Универсальный скрипт установки и запуска =====
echo.

REM Переход в директорию скрипта
echo Переход в директорию скрипта: %~dp0
cd /d "%~dp0"
echo Текущая директория: %CD%
echo.

REM Проверка наличия Python
echo Проверка наличия Python...
set PYTHON_CMD=none

REM Проверяем разные варианты команды Python
echo 1. Проверка команды 'py'...
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    Команда 'py' работает!
    set PYTHON_CMD=py
    goto PYTHON_FOUND
)

echo 2. Проверка команды 'python'...
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    Команда 'python' работает!
    set PYTHON_CMD=python
    goto PYTHON_FOUND
)

echo 3. Проверка команды 'python3'...
python3 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    Команда 'python3' работает!
    set PYTHON_CMD=python3
    goto PYTHON_FOUND
)

:PYTHON_NOT_FOUND
color 0C
echo ========================================================================
echo ОШИБКА: Python не найден в системе!
echo.
echo Пожалуйста, установите Python:
echo 1. Скачайте Python с сайта https://www.python.org/downloads/
echo 2. При установке отметьте галочку "Add Python to PATH"
echo 3. Перезагрузите компьютер после установки
echo 4. Запустите этот скрипт снова
echo ========================================================================
echo.
pause
exit /b 1

:PYTHON_FOUND
color 0A
echo.
echo Python найден! Будет использоваться команда: %PYTHON_CMD%
echo.
%PYTHON_CMD% --version
echo.

REM Главное меню
:MAIN_MENU
cls
echo ===== GameDetector - Главное меню =====
echo.
echo 1. Установить зависимости
echo 2. Запустить программу (с визуализацией)
echo 3. Запустить в режиме отладки
echo 4. Диагностика
echo 5. Настройка
echo 6. Выход
echo.
set /p choice="Выберите действие (1-6): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto RUN
if "%choice%"=="3" goto DEBUG_RUN
if "%choice%"=="4" goto DIAGNOSTICS
if "%choice%"=="5" goto SETTINGS
if "%choice%"=="6" goto EXIT
goto MAIN_MENU

:INSTALL
cls
echo ===== Установка зависимостей =====
echo.
echo Установка необходимых пакетов для GameDetector...
echo.

REM Проверка наличия файла requirements.txt
if not exist requirements.txt (
    echo Файл requirements.txt не найден. Создаю...
    (
        echo opencv-python>=4.5.5
        echo numpy>=1.22.3
        echo pyautogui>=0.9.53
        echo pywin32>=303
        echo Pillow>=9.0.1
    ) > requirements.txt
    echo Файл requirements.txt создан успешно.
)

echo Установка пакетов из requirements.txt...
%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo.
    echo Ошибка при установке зависимостей.
    echo Проверьте соединение с интернетом и доступ к PyPI.
    echo.
    pause
    goto MAIN_MENU
)

echo.
echo Установка завершена успешно!
echo.
pause
goto MAIN_MENU

:RUN
cls
echo ===== Запуск программы =====
echo.
echo Запуск GameDetector с визуализацией...
echo.
echo Инструкция по использованию:
echo - ESC: выход из программы
echo - V: включить/выключить визуализацию
echo - C: калибровка цветов
echo - S: сохранение настроек
echo - P: запуск инструмента выбора цветов
echo - W: переключиться на следующее окно
echo - Q: переключиться на предыдущее окно
echo - L: показать/скрыть список доступных окон
echo.
echo В отдельном окне будет показана визуализация распознанных объектов:
echo - ФИОЛЕТОВЫЙ: ваш персонаж 
echo - ЗЕЛЕНЫЙ: цель
echo - КРАСНЫЙ: ловушки
echo.
echo ВАЖНО: 
echo 1. Убедитесь, что целевое окно запущено и видно на экране
echo 2. Вы можете переключаться между окнами прямо во время работы программы (клавиши W, Q)
echo 3. Для просмотра списка доступных окон нажмите L
echo 4. Для выхода нажмите ESC или закройте консоль
echo 5. Если окно визуализации закрывается, вы можете открыть его снова клавишей V
echo.
echo Нажмите любую клавишу для запуска программы...
pause > nul

REM Проверяем наличие файла game_detector.py
if not exist game_detector.py (
    color 0C
    echo ОШИБКА: Файл game_detector.py не найден!
    echo Убедитесь, что вы запускаете скрипт из правильной директории.
    echo.
    pause
    goto MAIN_MENU
)

REM Запуск программы в отдельном окне cmd, чтобы оно не закрывалось при ошибке
start /wait cmd /k "%PYTHON_CMD% game_detector.py & if %ERRORLEVEL% NEQ 0 (color 0C & echo. & echo ОШИБКА: Программа завершилась с ошибкой! & echo. & pause) else (exit)"
goto MAIN_MENU

:DEBUG_RUN
cls
echo ===== Запуск в режиме отладки =====
echo.
echo Этот режим запускает программу с подробным выводом всех ошибок
echo и пытается выполнить программу несколькими методами, если основной метод не работает.
echo.
echo Также в этом режиме будет показана визуализация распознанных объектов,
echo чтобы вы могли видеть, что именно программа обнаруживает на экране.
echo.
echo Управление в режиме отладки:
echo - ESC: выход
echo - V: включить/выключить окно визуализации
echo - C: калибровка цветов
echo - S: сохранение настроек
echo.

REM Проверяем наличие debug_run.py, если нет - создаем
if not exist debug_run.py (
    echo Файл debug_run.py не найден. Создаю...
    (
        echo """
        echo Отладочный скрипт для запуска game_detector.py с подробным выводом ошибок
        echo """
        echo.
        echo import sys
        echo import os
        echo import traceback
        echo.
        echo # Определение команды Python (будет заменено game_setup.bat)
        echo PYTHON_CMD = "py"  # По умолчанию используем py, но скрипт заменит на правильную команду
        echo.
        echo print("=== Запуск game_detector.py в режиме отладки ===")
        echo print(f"Текущая директория: {os.getcwd()}")
        echo print(f"Используемая команда Python: {PYTHON_CMD}")
        echo.
        echo # Проверка наличия файла
        echo if not os.path.isfile("game_detector.py"):
        echo     print("ОШИБКА: Файл game_detector.py не найден в текущей директории!")
        echo     print(f"Содержимое директории: {os.listdir('.')}")
        echo     input("Нажмите Enter для выхода...")
        echo     sys.exit(1)
        echo.
        echo # Попытка запуска с отловом ошибок
        echo try:
        echo     print("\nЗапуск...")
        echo     
        echo     # Вариант 1: Импорт и выполнение основной функции
        echo     try:
        echo         print("Метод 1: Импорт модуля...")
        echo         from game_detector import GameDetector
        echo         
        echo         print("Создание экземпляра GameDetector...")
        echo         detector = GameDetector()
        echo         
        echo         print("Запуск метода run()...")
        echo         detector.run()
        echo     except Exception as e1:
        echo         print(f"\nМетод 1 завершился с ошибкой: {e1}")
        echo         print("Трассировка ошибки метода 1:")
        echo         traceback.print_exc()
        echo         
        echo         # Вариант 2: Выполнение через exec
        echo         print("\nПробую метод 2: Выполнение через exec...")
        echo         try:
        echo             with open("game_detector.py", "r", encoding="utf-8") as f:
        echo                 code = compile(f.read(), "game_detector.py", "exec")
        echo                 exec(code)
        echo         except Exception as e2:
        echo             print(f"\nМетод 2 завершился с ошибкой: {e2}")
        echo             print("Трассировка ошибки метода 2:")
        echo             traceback.print_exc()
        echo             
        echo             # Вариант 3: Запуск через os.system
        echo             print("\nПробую метод 3: Запуск через os.system...")
        echo             exit_code = os.system(f"{PYTHON_CMD} game_detector.py")
        echo             if exit_code != 0:
        echo                 print(f"\nМетод 3 завершился с кодом ошибки: {exit_code}")
        echo             
        echo except Exception as e:
        echo     print(f"\nГлобальная ошибка: {e}")
        echo     traceback.print_exc()
        echo.
        echo print("\n=== Отладка завершена ===")
        echo print("Если вы видите ошибки, сообщите их для дальнейшей диагностики.")
        echo input("Нажмите Enter для выхода...")
    ) > debug_run.py
    echo Файл debug_run.py создан успешно.
)

echo Запуск программы в режиме отладки...
echo Это позволит увидеть подробную информацию об ошибках.
echo.

REM Проверка, какая версия Питона будет использоваться для запуска скрипта отладки
set DEBUG_PY_CMD=%PYTHON_CMD%
echo Будет использована команда: %DEBUG_PY_CMD%

REM Заменяем переменную Python в скрипте отладки
powershell -Command "(Get-Content debug_run.py) -replace 'PYTHON_CMD = \"py\"', 'PYTHON_CMD = \"%DEBUG_PY_CMD%\"' | Set-Content debug_run.py"

REM Запуск отладочного скрипта
%DEBUG_PY_CMD% debug_run.py
echo.
pause
goto MAIN_MENU

:DIAGNOSTICS
cls
echo ===== Диагностика =====
echo.
echo 1. Проверка зависимостей
echo 2. Проверка библиотеки pywin32
echo 3. Проверка файла game_detector.py
echo 4. Установить заглушку для notification.py (при проблемах с pywin32)
echo 5. Восстановить оригинальный notification.py
echo 6. Вернуться в главное меню
echo.
set /p diag_choice="Выберите действие (1-6): "

if "%diag_choice%"=="1" goto CHECK_DEPS
if "%diag_choice%"=="2" goto CHECK_PYWIN32
if "%diag_choice%"=="3" goto CHECK_GAME_DETECTOR
if "%diag_choice%"=="4" goto INSTALL_NOTIFICATION_STUB
if "%diag_choice%"=="5" goto RESTORE_NOTIFICATION
if "%diag_choice%"=="6" goto MAIN_MENU
goto DIAGNOSTICS

:CHECK_DEPS
cls
echo ===== Проверка зависимостей =====
echo.
echo Проверка установленных пакетов Python...
echo.
%PYTHON_CMD% -m pip list | findstr opencv-python
%PYTHON_CMD% -m pip list | findstr numpy
%PYTHON_CMD% -m pip list | findstr pyautogui
%PYTHON_CMD% -m pip list | findstr pywin32
%PYTHON_CMD% -m pip list | findstr Pillow
echo.
pause
goto DIAGNOSTICS

:CHECK_PYWIN32
cls
echo ===== Проверка библиотеки pywin32 =====
echo.

REM Создаем временный скрипт для проверки pywin32, если его нет
if not exist check_pywin32.py (
    echo Создание скрипта для проверки pywin32...
    (
        echo import os, sys, traceback
        echo print("=== Базовая проверка pywin32 ===")
        echo try:
        echo     import win32gui
        echo     print("win32gui импортирован успешно!")
        echo     print("\nПопытка перечислить окна:")
        echo     try:
        echo         def callback(hwnd, ctx):
        echo             if win32gui.IsWindowVisible(hwnd):
        echo                 title = win32gui.GetWindowText(hwnd)
        echo                 if title: print(f"  {hwnd}: {title}")
        echo             return True
        echo         win32gui.EnumWindows(callback, None)
        echo     except Exception as e:
        echo         print(f"ОШИБКА при перечислении окон: {e}")
        echo         traceback.print_exc()
        echo except ImportError:
        echo     print("ОШИБКА: Не удалось импортировать win32gui")
        echo     print("Рекомендуется переустановить pywin32:")
        echo     print("%PYTHON_CMD% -m pip install --upgrade --force-reinstall pywin32")
        echo except Exception as e:
        echo     print(f"Неизвестная ошибка: {e}")
        echo     traceback.print_exc()
        echo print("\nНажмите Enter для выхода...")
        echo input()
    ) > check_pywin32.py
)

%PYTHON_CMD% check_pywin32.py
echo.
echo Если у вас проблемы с pywin32:
echo 1. Попробуйте переустановить: %PYTHON_CMD% -m pip install --upgrade --force-reinstall pywin32
echo 2. Запустите скрипт pywin32_postinstall.py с правами администратора (если доступен)
echo 3. Если проблемы остаются, используйте заглушку для notification.py из меню диагностики
echo.
pause
goto DIAGNOSTICS

:CHECK_GAME_DETECTOR
cls
echo ===== Проверка файла game_detector.py =====
echo.

REM Проверка наличия файла game_detector.py
if not exist game_detector.py (
    echo ОШИБКА: Файл game_detector.py не найден!
    echo Текущая директория: %CD%
    echo Содержимое директории:
    dir
    echo.
    pause
    goto DIAGNOSTICS
)

echo Проверка синтаксиса файла game_detector.py...
%PYTHON_CMD% -m py_compile game_detector.py
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: В файле game_detector.py обнаружены синтаксические ошибки!
) else (
    echo Синтаксис файла game_detector.py проверен, ошибок не обнаружено.
)
echo.
pause
goto DIAGNOSTICS

:INSTALL_NOTIFICATION_STUB
cls
echo ===== Установка заглушки для notification.py =====
echo.

REM Проверка наличия файла notification_stub.py
if not exist notification_stub.py (
    echo Создание файла notification_stub.py...
    (
        echo """
        echo Упрощенная версия модуля уведомлений без использования win32gui
        echo Используйте эту версию, если у вас проблемы с pywin32
        echo """
        echo.
        echo import logging
        echo import time
        echo import os
        echo.
        echo class GameNotification:
        echo     """
        echo     Класс для отображения простых консольных уведомлений
        echo     Заменяет GUI-версию при проблемах с библиотеками Windows
        echo     """
        echo     
        echo     def __init__(self, title="GameDetector", position='top-right', duration=3.0, sound=False):
        echo         """
        echo         Инициализация уведомления
        echo         
        echo         Args:
        echo             title (str): Заголовок уведомления
        echo             position (str): Позиция уведомления (игнорируется в этой версии)
        echo             duration (float): Длительность отображения в секундах
        echo             sound (bool): Проигрывать ли звук при показе уведомления
        echo         """
        echo         self.title = title
        echo         self.position = position
        echo         self.duration = duration
        echo         self.sound = sound
        echo         self.is_showing = False
        echo         logging.info(f"Инициализирован класс уведомлений (STUB). Заголовок: {title}")
        echo     
        echo     def show(self, message, bg_color="#3366FF", fg_color="white"):
        echo         """
        echo         Показать уведомление в консоли
        echo         
        echo         Args:
        echo             message (str): Текст уведомления
        echo             bg_color (str): Цвет фона (игнорируется в консольном режиме)
        echo             fg_color (str): Цвет текста (игнорируется в консольном режиме)
        echo         """
        echo         os.system("cls" if os.name == "nt" else "clear")
        echo         border = "=" * (len(self.title) + len(message) + 10)
        echo         print("\n\n")
        echo         print(border)
        echo         print(f"| {self.title}: {message} |")
        echo         print(border)
        echo         print("\n")
        echo         
        echo         self.is_showing = True
        echo         logging.info(f"Показано уведомление (STUB): {message}")
        echo         
        echo         # Имитация автоматического закрытия уведомления
        echo         if self.duration > 0:
        echo             time.sleep(0.5)  # Короткая задержка
        echo             self.close()
        echo     
        echo     def close(self):
        echo         """Закрыть уведомление (просто меняет флаг)"""
        echo         if self.is_showing:
        echo             self.is_showing = False
        echo             logging.info("Уведомление (STUB) закрыто")
        echo.
        echo.
        echo if __name__ == "__main__":
        echo     # Пример использования
        echo     print("Тестирование заглушки уведомлений...")
        echo     notifier = GameNotification("Тест")
        echo     notifier.show("Это тестовое уведомление")
        echo     print("Тест завершен.")
    ) > notification_stub.py
    echo Файл notification_stub.py создан успешно.
)

REM Создаем резервную копию текущего файла notification.py, если он существует
if exist notification.py (
    echo Сохранение резервной копии оригинального notification.py...
    if not exist notification.py.bak (
        copy notification.py notification.py.bak
        echo Резервная копия создана: notification.py.bak
    ) else (
        echo Резервная копия уже существует (notification.py.bak).
    )
)

REM Копируем заглушку на место основного файла
echo Установка заглушки notification_stub.py...
copy notification_stub.py notification.py
echo.
echo Заглушка установлена успешно!
echo.
pause
goto DIAGNOSTICS

:RESTORE_NOTIFICATION
cls
echo ===== Восстановление оригинального notification.py =====
echo.

if exist notification.py.bak (
    echo Восстановление оригинального notification.py из резервной копии...
    copy notification.py.bak notification.py
    echo Файл notification.py восстановлен.
) else (
    echo Резервная копия notification.py.bak не найдена!
    echo Невозможно восстановить оригинальный файл.
)

echo.
pause
goto DIAGNOSTICS

:SETTINGS
cls
echo ===== Настройки =====
echo.
echo 1. Настроить цвета (калибровка)
echo 2. Выбор цветов (инструмент выбора)
echo 3. Настроить целевое окно
echo 4. Создать заглушку notification.py (без GUI)
echo 5. Восстановить оригинальный notification.py
echo 6. Вернуться в главное меню
echo.
set /p settings_choice="Выберите действие (1-6): "

if "%settings_choice%"=="1" goto COLOR_CALIBRATION
if "%settings_choice%"=="2" goto COLOR_PICKER
if "%settings_choice%"=="3" goto CONFIGURE_TARGET_WINDOW
if "%settings_choice%"=="4" goto INSTALL_NOTIFICATION_STUB
if "%settings_choice%"=="5" goto RESTORE_NOTIFICATION
if "%settings_choice%"=="6" goto MAIN_MENU
goto SETTINGS

:CONFIGURE_TARGET_WINDOW
cls
echo ===== Настройка целевого окна =====
echo.
echo Текущая настройка: поиск окна с заголовком "BlueStacks"
echo.
echo Вы можете изменить название окна, на котором будет фокусироваться программа.
echo Например, если вы используете другой эмулятор или игру в окне.
echo.
echo Доступные окна на вашем компьютере:
%PYTHON_CMD% -c "import win32gui; def callback(hwnd, ctx): print(f'ID:{hwnd} - {win32gui.GetWindowText(hwnd)}' if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) else ''); return True; win32gui.EnumWindows(callback, None)"
echo.
echo Введите новое название окна (или часть заголовка):
set /p new_window_title="Название окна: "

if "%new_window_title%"=="" (
    echo Ошибка: название окна не может быть пустым.
    pause
    goto SETTINGS
)

REM Создаем временный скрипт для изменения названия окна в game_detector.py
echo import re > update_window_title.py
echo with open("game_detector.py", "r", encoding="utf-8") as f: >> update_window_title.py
echo     content = f.read() >> update_window_title.py
echo new_content = re.sub(r'self\.window_title = "[^"]*"', f'self.window_title = "%new_window_title%"', content) >> update_window_title.py
echo with open("game_detector.py", "w", encoding="utf-8") as f: >> update_window_title.py
echo     f.write(new_content) >> update_window_title.py
echo print(f"Целевое окно изменено на: {new_window_title}") >> update_window_title.py

%PYTHON_CMD% update_window_title.py
del update_window_title.py

echo.
echo Настройка целевого окна завершена.
echo При следующем запуске программа будет искать окно с названием "%new_window_title%".
echo.
pause
goto SETTINGS

:COLOR_CALIBRATION
cls
echo ===== Калибровка цветов =====
echo.

REM Проверка существования game_detector.py
if not exist game_detector.py (
    echo ОШИБКА: Файл game_detector.py не найден!
    echo Невозможно запустить калибровку цветов.
    echo.
    pause
    goto SETTINGS
)

echo Запуск калибровки цветов...
echo Будет открыто окно калибровки цветов для настройки распознавания.
echo.
echo Инструкция:
echo - Используйте ползунки для настройки цветовых диапазонов
echo - Настройте так, чтобы нужные объекты отображались на правом экране
echo - Нажмите ESC для завершения калибровки
echo.
echo Нажмите любую клавишу для запуска...
pause > nul

start /wait cmd /k "%PYTHON_CMD% -c "from game_detector import GameDetector; detector = GameDetector(); detector.calibrate_colors()" & pause"
echo.
pause
goto SETTINGS

:COLOR_PICKER
cls
echo ===== Запуск утилиты выбора цветов =====
echo.

REM Проверка существования color_picker.py
if not exist color_picker.py (
    echo ОШИБКА: Файл color_picker.py не найден!
    echo Невозможно запустить утилиту выбора цветов.
    echo.
    pause
    goto SETTINGS
)

echo Запуск утилиты выбора цветов...
echo Это запустит инструмент для выбора цветов из изображения.
echo.
echo Нажмите любую клавишу для запуска...
pause > nul

start /wait cmd /k "%PYTHON_CMD% color_picker.py & pause"
echo.
pause
goto SETTINGS

:EXIT
cls
echo ===== Выход =====
echo.
echo Спасибо за использование GameDetector!
echo.
echo Нажмите любую клавишу для выхода...
pause > nul
exit /b 0 