#!/bin/bash

echo "🚀 Установка зависимостей для системы обработки APK/XAPK файлов"

# Обновляем pip
echo "📦 Обновляем pip..."
python3 -m pip install --upgrade pip

# Устанавливаем зависимости Python
echo "🐍 Устанавливаем зависимости Python..."
pip3 install playwright==1.40.0
pip3 install mysql-connector-python==8.2.0

# Устанавливаем браузеры для Playwright
echo "🌐 Устанавливаем браузеры для Playwright..."
python3 -m playwright install chromium

# Проверяем установку
echo "✅ Проверяем установку..."
python3 -c "import playwright; print('Playwright установлен успешно')"
python3 -c "import mysql.connector; print('MySQL connector установлен успешно')"

echo "🎉 Все зависимости установлены успешно!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Создайте конфигурационный файл: cp config_example.py config.py"
echo "2. Отредактируйте config.py с вашими настройками базы данных"
echo "3. Создайте таблицы в БД: mysql -u user -p database < setup_database.sql"
echo "4. Запустите скрипт: python3 step5_file_processor.py"

