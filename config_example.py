#!/usr/bin/env python3
"""
Пример конфигурационного файла
Скопируйте этот файл в config.py и заполните реальными данными
"""

# Конфигурация базы данных
DB_CONFIG = {
    'host': 'localhost',           # Хост базы данных
    'database': 'your_database',   # Имя базы данных
    'user': 'your_username',       # Имя пользователя
    'password': 'your_password',   # Пароль
    'port': 3306,                  # Порт (обычно 3306 для MySQL)
    'charset': 'utf8mb4',
    'autocommit': True
}

# Пути к файлам
LINKS_FILE = "step4_links.txt"                    # Файл со ссылками
BASE_DOWNLOAD_DIR = "/www/n2.anplus1.com/files"  # Базовая папка для загрузок

# Настройки парсера
PARSER_CONFIG = {
    'timeout': 60000,              # Таймаут для загрузки страниц (мс)
    'cloudflare_wait': 120,        # Максимальное время ожидания Cloudflare (сек)
    'download_wait': 30,           # Время ожидания начала загрузки (сек)
    'headless': True,              # Запуск браузера в headless режиме
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Настройки для dle_files
DLE_FILES_CONFIG = {
    'author': 'app4ok',            # Автор файлов
    'driver': 2,                   # Драйвер (обычно 2)
    'is_public': 0                 # Публичность файла (0 - приватный)
}

