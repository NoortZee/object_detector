@echo off
title Установка и запуск GameDetector
color 0A

REM Добавляем задержку в начало, чтобы окно не закрывалось при ошибке
ping -n 1 127.0.0.1 > nul

echo ===== GameDetector - Установка и Запуск =====
echo.

REM Проверка наличия Python с генерацией ошибки, чтобы увидеть, доходит ли выполнение до этого места
echo Проверка наличия Python...
where py >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    color 0C
    echo ОШИБКА: Python (команда 'py') не найден в системе!
    echo Установите Python с сайта https://www.python.org/downloads/
    echo и убедитесь, что в процессе установки вы отметили галочку "Add Python to PATH".
    echo.
    echo Если Python уже установлен, но команда 'py' не работает, попробуйте:
    echo 1. Перезапустить компьютер (если вы только что установили Python)
    echo 2. Добавить Python в переменную среды PATH вручную
    echo 3. Использовать полный путь к Python, например: C:\Path\To\Python\python.exe
    echo.
    pause
    exit /b 1
)

echo Python найден успешно! Используется команда 'py'.
echo.

REM Проверка версии Python
echo Версия Python:
py --version
echo.

REM Переход в директорию скрипта
echo Переход в директорию скрипта: %~dp0
cd /d "%~dp0"
echo Текущая директория: %CD%
echo.
pause

:MENU
cls
echo ===== GameDetector - Установка и Запуск =====
echo.
echo Внимание! В вашей системе для запуска Python используется команда 'py', а не 'python'.
echo.
echo Выберите действие:
echo 1. Установить зависимости и запустить программу
echo 2. Запустить программу (без установки зависимостей)
echo 3. Проверить зависимости
echo 4. Протестировать импорты модулей
echo 5. Полная диагностика
echo 6. Запустить программу в отладочном режиме (подробный вывод ошибок)
echo 7. Выход
echo.
set /p choice="Ваш выбор (1-7): "

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto RUN
if "%choice%"=="3" goto CHECK_DEPS
if "%choice%"=="4" goto TEST_IMPORTS
if "%choice%"=="5" goto DIAGNOSTICS
if "%choice%"=="6" goto DEBUG_RUN
if "%choice%"=="7" goto EXIT
goto MENU

:INSTALL
echo.
echo Установка необходимых пакетов для детектора объектов...
py -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ошибка при установке зависимостей.
    echo Проверьте соединение с интернетом и доступ к PyPI.
    echo.
    pause
    goto MENU
)
echo.
echo Установка завершена успешно!
goto RUN

:RUN
echo.
echo Запуск программы...
echo.
echo Инструкция по использованию:
echo - ESC: выход из программы
echo - C: калибровка цветов
echo - S: сохранение настроек
echo - P: запуск инструмента выбора цветов
echo.
echo Нажмите Enter для запуска...
pause > nul

REM Запуск программы с помощью start /wait, чтобы окно не закрывалось
echo Запуск game_detector.py...
start /wait cmd /k "py game_detector.py & if %ERRORLEVEL% NEQ 0 (color 0C & echo. & echo ОШИБКА: Программа завершилась с ошибкой! & echo. & pause) else (exit)"
goto MENU

:CHECK_DEPS
echo.
echo Проверка установленных зависимостей...
echo.
py -m pip list | findstr opencv-python
py -m pip list | findstr numpy
py -m pip list | findstr pyautogui
py -m pip list | findstr Pillow
py -m pip list | findstr pywin32
py -m pip list | findstr pytesseract
echo.
pause
goto MENU

:TEST_IMPORTS
echo.
echo Тестирование импортов модулей...
echo.
py test_imports.py
goto MENU

:DIAGNOSTICS
echo.
echo Запуск полной диагностики...
echo.
py check_environment.py
pause
goto MENU

:DEBUG_RUN
echo.
echo Запуск программы в отладочном режиме...
echo.
if not exist debug_run.py (
    echo ОШИБКА: Файл debug_run.py не найден!
    echo Возможно, вам нужно обновить файлы диагностики.
    pause
    goto MENU
)
py debug_run.py
goto MENU

:EXIT
echo.
echo До свидания!
ping -n 2 127.0.0.1 > nul 