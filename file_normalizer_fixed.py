#!/usr/bin/env python3
"""
Система обработки файлов из step4_links.txt
Скачивает файлы через парсер apkcombo и обновляет базу данных
"""
import asyncio
import os
import sys
import hashlib
import time
from pathlib import Path
from datetime import datetime
import mysql.connector
from mysql.connector import Error
import re
from playwright.async_api import async_playwright
import unicodedata

# Конфигурация базы данных
DB_CONFIG = {
    'host': '79.174.12.174',
    'database': 'ook',  # Замените на реальное имя БД
    'user': 'ook',           # Замените на реальный логин
    'password': 'LqDP2vrZznr8vxJI7RzN'        # Замените на реальный пароль
}

# Путь к файлу со ссылками
LINKS_FILE = "step4_links.txt"
# Базовая папка для загрузок (формат: год-месяц)
BASE_DOWNLOAD_DIR = "/www/n2.anplus1.com/files"

# Создаем таблицу для отслеживания скачанных файлов
CREATE_TRACKING_TABLE = """
CREATE TABLE IF NOT EXISTS file_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    news_id INT NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    version VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    checksum VARCHAR(32) NOT NULL,
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    source_url VARCHAR(500) NOT NULL,
    INDEX idx_news_id (news_id),
    INDEX idx_app_name (app_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
"""

class FileProcessor:
    def __init__(self):
        self.connection = None
        self.download_dir = self.get_current_download_dir()

    def get_current_download_dir(self):
        """Получаем папку для текущего месяца в формате год-месяц"""
        now = datetime.now()
        month_dir = f"{now.year}-{now.month:02d}"
        full_path = Path(BASE_DOWNLOAD_DIR) / month_dir
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path

    def connect_db(self):
        """Подключение к базе данных"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("✅ Подключение к базе данных установлено")

                # Создаем таблицу отслеживания если не существует
                cursor = self.connection.cursor()
                cursor.execute(CREATE_TRACKING_TABLE)
                self.connection.commit()
                cursor.close()

                return True
        except Error as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            return False

    def disconnect_db(self):
        """Отключение от базы данных"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Соединение с базой данных закрыто")

    def calculate_checksum(self, file_path):
        """Вычисляем MD5 чексумму файла"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def transliterate_cyrillic(self, text):
        """Транслитерация кириллицы в латиницу"""
        cyrillic_to_latin = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
            'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
            'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
            'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
            'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        }
        
        result = ''
        for char in text:
            if char in cyrillic_to_latin:
                result += cyrillic_to_latin[char]
            else:
                result += char
        return result

    def normalize_filename(self, filename):
        """Нормализуем имя файла согласно требованиям"""
        print(f"📝 Исходное имя файла: {filename}")

        # Убираем "_apkcombo.com" из названия
        filename = filename.replace('_apkcombo.com', '')

        # Разделяем имя файла и расширение
        name_part, extension = os.path.splitext(filename)

        # Транслитерируем кириллицу
        name_part = self.transliterate_cyrillic(name_part)

        # Приводим к нижнему регистру
        name_part = name_part.lower()
        extension = extension.lower()

        # Убираем специальные символы и заменяем на подчеркивания
        name_part = re.sub(r'[+\-\s]+', '_', name_part)
        
        # Заменяем точки на подчеркивания в имени файла (но не в расширении)
        name_part = name_part.replace('.', '_')
        
        # Убираем множественные подчеркивания
        name_part = re.sub(r'_+', '_', name_part)
        
        # Убираем подчеркивания в начале и конце
        name_part = name_part.strip('_')

        # Собираем обратно с одной точкой перед расширением
        normalized_filename = f"{name_part}{extension}"

        print(f"📝 Нормализованное имя: {normalized_filename}")
        return normalized_filename

    def format_filename_for_attachment(self, filename):
        """Форматируем имя файла для поля apk-original"""
        print(f"📝 Форматируем для attachment: {filename}")

        # Разделяем имя файла и расширение
        name_part, extension = os.path.splitext(filename)

        # Убираем подчеркивания и заменяем на пробелы
        name_part = name_part.replace('_', ' ')

        # Убираем лишние символы +-+
        name_part = name_part.replace('+-+', ' ')
        name_part = name_part.replace('+', ' ')
        name_part = name_part.replace('-', ' ')

        # Убираем множественные пробелы
        name_part = re.sub(r'\s+', ' ', name_part).strip()

        # Восстанавливаем точки в версии (ищем паттерны типа "1 8 3" и заменяем на "1.8.3")
        # Ищем последовательности цифр разделенных пробелами в конце строки
        version_pattern = r'(\d+)\s+(\d+)\s+(\d+)(?:\s+(\d+))?(?:\s+(\d+))?$'
        match = re.search(version_pattern, name_part)
        if match:
            # Заменяем найденную версию на правильный формат с точками
            version_parts = [part for part in match.groups() if part is not None]
            version_str = '.'.join(version_parts)
            name_part = re.sub(version_pattern, version_str, name_part)

        # Собираем обратно
        formatted_filename = f"{name_part}{extension}"

        print(f"📝 Отформатированное имя: {formatted_filename}")
        return formatted_filename

    def check_physical_file_exists(self, file_path):
        """Проверяем существует ли физический файл на диске"""
        if not file_path or not os.path.exists(file_path):
            print(f"❌ Физический файл не найден: {file_path}")
            return False
        
        # Проверяем что это действительно файл, а не папка
        if not os.path.isfile(file_path):
            print(f"❌ Путь не является файлом: {file_path}")
            return False
            
        # Проверяем размер файла (должен быть больше 0)
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            print(f"❌ Файл пустой: {file_path}")
            return False
            
        print(f"✅ Физический файл существует: {file_path} ({file_size} байт)")
        return True

    def parse_link_line(self, line):
        """Парсим строку из файла step4_links.txt"""
        # Формат: 1,[attachment=861:Apple Music_5.0.0.xapk],https://apkcombo.com/ru/apple-music/com.apple.android.music/
        line = line.strip()
        if not line:
            return None

        parts = line.split(',', 2)
        if len(parts) != 3:
            return None

        news_id = parts[0].strip()
        attachment_info = parts[1].strip()
        url = parts[2].strip()

        # Извлекаем информацию из attachment
        match = re.search(r'\[attachment=(\d+):([^\]]+)\]', attachment_info)
        if not match:
            return None

        old_file_id = match.group(1)
        filename = match.group(2)

        return {
            'news_id': int(news_id),
            'old_file_id': int(old_file_id),
            'filename': filename,
            'url': url
        }

    def check_if_update_needed(self, news_id, app_name, current_version):
        """Проверяем нужно ли обновлять файл"""
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT version, file_size, checksum, file_path
            FROM file_tracking
            WHERE news_id = %s AND app_name = %s
            ORDER BY last_updated DESC LIMIT 1
            """
            cursor.execute(query, (news_id, app_name))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                print(f"📝 Новое приложение {app_name} для новости {news_id}")
                return True, None

            stored_version = result[0]
            stored_file_path = result[3]
            
            # Проверяем физическое существование файла
            if not self.check_physical_file_exists(stored_file_path):
                print(f"🔄 Файл отсутствует на диске, нужно перекачать")
                return True, result

            if stored_version != current_version:
                print(f"🔄 Обновление нужно: {stored_version} -> {current_version}")
                return True, result
            else:
                print(f"✅ Версия {current_version} уже актуальна и файл существует")
                return False, result

        except Error as e:
            print(f"❌ Ошибка проверки версии: {e}")
            return True, None

    def extract_version_from_filename(self, filename):
        """Извлекаем версию из имени файла ДО нормализации"""
        print(f"🔍 Извлекаем версию из: {filename}")
        
        # Ищем паттерн версии в имени файла
        version_patterns = [
            r'[_\s\-](\d+\.\d+\.\d+\.\d+)',  # _1.8.3.0
            r'[_\s\-](\d+\.\d+\.\d+)',       # _1.8.3
            r'[_\s\-](\d+\.\d+)',            # _1.8
            r'v(\d+\.\d+\.\d+\.\d+)',        # v1.8.3.0
            r'v(\d+\.\d+\.\d+)',             # v1.8.3
            r'v(\d+\.\d+)',                  # v1.8
            r'(\d+\.\d+\.\d+\.\d+)',         # 1.8.3.0
            r'(\d+\.\d+\.\d+)',              # 1.8.3
            r'(\d+\.\d+)',                   # 1.8
        ]

        for pattern in version_patterns:
            match = re.search(pattern, filename)
            if match:
                version = match.group(1)
                print(f"✅ Найдена версия: {version}")
                return version

        print("⚠️ Версия не найдена, используем 1.0.0")
        return "1.0.0"  # Версия по умолчанию

    def extract_app_name_from_filename(self, filename):
        """Извлекаем название приложения из имени файла ДО нормализации"""
        print(f"🔍 Извлекаем название из: {filename}")
        
        # Убираем расширение
        name = filename.replace('.xapk', '').replace('.apk', '')
        
        # Убираем версию если есть
        version_patterns = [
            r'[_\s\-]\d+\.\d+\.\d+\.\d+.*$',
            r'[_\s\-]\d+\.\d+\.\d+.*$',
            r'[_\s\-]\d+\.\d+.*$',
            r'v\d+\.\d+\.\d+\.\d+.*$',
            r'v\d+\.\d+\.\d+.*$',
            r'v\d+\.\d+.*$',
        ]
        
        for pattern in version_patterns:
            name = re.sub(pattern, '', name)
        
        # Очищаем от лишних символов
        name = re.sub(r'[_\-\+\s]+$', '', name)
        
        app_name = name.strip()
        print(f"✅ Название приложения: {app_name}")
        return app_name

    async def wait_for_cloudflare(self, page, max_wait=120):
        """Ждем прохождения проверки Cloudflare"""
        print("🔄 Проверяем наличие Cloudflare...")
        for i in range(max_wait):
            await asyncio.sleep(1)
            try:
                current_url = page.url
                page_title = await page.title()
                # Проверяем индикаторы Cloudflare
                cf_indicators = [
                    "div.cf-browser-verification",
                    "div.cf-checking-browser",
                    "[data-ray]",
                    "h1:has-text('Checking your browser')",
                    "h1:has-text('Just a moment')"
                ]
                is_cf_active = False
                for indicator in cf_indicators:
                    try:
                        element = await page.query_selector(indicator)
                        if element:
                            is_cf_active = True
                            break
                    except:
                        continue
                # Проверяем по заголовку и URL
                if ("just a moment" in page_title.lower() or
                    "checking" in page_title.lower() or
                    "cloudflare" in current_url.lower()):
                    is_cf_active = True
                if not is_cf_active:
                    print("✅ Cloudflare проверка пройдена или отсутствует")
                    return True
                if i % 10 == 0:
                    print(f"⏳ Ждем Cloudflare... ({i+1}/{max_wait})")
            except Exception as e:
                print(f"   Ошибка при проверке Cloudflare: {e}")
                continue
        print("⚠️ Превышено время ожидания Cloudflare")
        return False

    async def download_file_from_r2_url(self, page, r2_url):
        """Скачиваем файл по r2 ссылке"""
        print(f"🔗 Переходим по r2 ссылке для скачивания...")
        # Устанавливаем обработчик загрузки ДО перехода на страницу
        download_started = False
        download_obj = None

        async def handle_download(download):
            nonlocal download_started, download_obj
            download_obj = download
            download_started = True
            print("🎯 Загрузка началась!")

        page.on("download", handle_download)

        # Пытаемся перейти на страницу, но ожидаем, что может начаться загрузка
        try:
            await page.goto(r2_url, wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            if "Download is starting" in str(e):
                print("✅ Загрузка началась сразу при переходе")
                await asyncio.sleep(2)
            else:
                raise e

        # Если загрузка не началась сразу, ждем прохождения Cloudflare
        if not download_started:
            print("🔄 Загрузка не началась сразу, проверяем Cloudflare...")
            await self.wait_for_cloudflare(page, max_wait=120)
            # Ждем начала загрузки еще немного
            for i in range(30):
                if download_started:
                    break
                await asyncio.sleep(1)
                if i % 5 == 0:
                    print(f"   Ждем загрузку... ({i+1}/30)")

        if not download_started:
            raise Exception("Загрузка так и не началась")

        print("📥 Ждем завершения загрузки...")

        # Определяем имя файла
        suggested_filename = download_obj.suggested_filename
        if not suggested_filename:
            # Пытаемся извлечь из URL
            if "filename" in r2_url:
                match = re.search(r'filename%253D%2522([^%]+)', r2_url)
                if match:
                    suggested_filename = match.group(1).replace('%2520', ' ')
                else:
                    suggested_filename = "downloaded_file.apk"
            else:
                suggested_filename = "downloaded_file.apk"

        print(f"📁 Исходное имя файла: {suggested_filename}")

        # Нормализуем имя файла
        normalized_filename = self.normalize_filename(suggested_filename)

        # Сохраняем файл с нормализованным именем
        final_file = self.download_dir / normalized_filename
        await download_obj.save_as(str(final_file))

        # Проверяем результат
        if final_file.exists():
            size_mb = final_file.stat().st_size / 1024 / 1024
            print(f"✅ Файл успешно скачан: {final_file}")
            print(f"📊 Размер файла: {size_mb:.2f} MB")
            return final_file
        else:
            print("❌ Файл не был сохранен")
            return None

    async def download_from_apkcombo(self, app_url):
        """Скачиваем файл с apkcombo.com"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage"
                ]
            )
            context = await browser.new_context(
                accept_downloads=True,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                print(f"📱 Открываем страницу приложения: {app_url}")
                await page.goto(app_url, wait_until="domcontentloaded", timeout=60000)
                # Ждем прохождения Cloudflare если есть
                await self.wait_for_cloudflare(page, max_wait=60)
                await asyncio.sleep(3)

                # Шаг 1: Ищем ссылку "Скачать APK"
                print("🔍 Ищем ссылку 'Скачать APK'...")
                download_link = None
                selectors_to_try = [
                    "a.button.is-success.is-fullwidth",
                    "a.button.is-success",
                    "a[href*='/download/apk']",
                    "a[href*='/download/']",
                    "div.download a.button"
                ]
                for selector in selectors_to_try:
                    try:
                        print(f"   Пробуем селектор: {selector}")
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            href = await element.get_attribute("href")
                            text = await element.inner_text()
                            print(f"     Найден элемент: href={href}, text={text.strip()[:30]}")
                            if href and ('/download/' in href or 'apk' in href.lower()):
                                download_link = element
                                print(f"   ✅ Выбран элемент с href: {href}")
                                break
                        if download_link:
                            break
                    except Exception as e:
                        print(f"     Ошибка с селектором {selector}: {e}")
                        continue
                if not download_link:
                    raise Exception("Не удалось найти ссылку 'Скачать APK'")

                href = await download_link.get_attribute("href")
                if not href:
                    raise Exception("Не удалось получить href ссылки")
                # Приводим ссылку к полному виду
                if href.startswith('/'):
                    download_page_url = f"https://apkcombo.com{href}"
                else:
                    download_page_url = href
                print(f"➡️ Ссылка на страницу загрузки: {download_page_url}")

                # Шаг 2: Переходим на страницу загрузки
                await page.goto(download_page_url, wait_until="domcontentloaded", timeout=120000)
                await self.wait_for_cloudflare(page, max_wait=60)
                await asyncio.sleep(5)

                # Шаг 3: Ищем первый вариант файла в ul.file-list
                print("🔍 Ищем первый вариант файла в ul.file-list...")
                variant_selectors = [
                    "ul.file-list li a",
                    "ul.file-list a",
                    ".file-list li a",
                    ".file-list a"
                ]
                variant = None
                for selector in variant_selectors:
                    try:
                        print(f"   Ищем варианты с селектором: {selector}")
                        variant = await page.wait_for_selector(selector, timeout=15000)
                        if variant:
                            print(f"   ✅ Найден вариант с селектором: {selector}")
                            break
                    except:
                        continue
                if not variant:
                    raise Exception("Не удалось найти варианты загрузки в ul.file-list")

                # Получаем информацию о файле
                try:
                    file_type_element = await variant.query_selector("span.vtype span, .type-apk, .type-xapk")
                    file_type = await file_type_element.inner_text() if file_type_element else "APK"
                    version_element = await variant.query_selector("span.vername")
                    version = await version_element.inner_text() if version_element else "Unknown"
                    print(f"📦 Найден файл: {version} ({file_type})")
                except:
                    file_type = "APK"
                    version = "Unknown"

                # Получаем r2 ссылку
                r2_href = await variant.get_attribute("href")
                if not r2_href:
                    raise Exception("Не удалось найти r2 ссылку варианта загрузки")

                # Приводим r2 ссылку к полному виду
                if r2_href.startswith('/'):
                    r2_url = f"https://apkcombo.com{r2_href}"
                else:
                    r2_url = r2_href
                print(f"🔗 Найдена r2 ссылка: {r2_url}")

                # Шаг 4: Скачиваем файл по r2 ссылке
                downloaded_file = await self.download_file_from_r2_url(page, r2_url)
                return downloaded_file, version
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                print(f"🔍 Текущий URL: {page.url}")
                # Сохраняем скриншот для отладки
                try:
                    await page.screenshot(path="debug_screenshot.png", full_page=True)
                    print("📸 Скриншот сохранен: debug_screenshot.png")
                except:
                    pass
                return None, None
            finally:
                await context.close()
                await browser.close()
                print("🔒 Браузер закрыт")

    def add_to_dle_files(self, news_id, filename, file_path, file_size, checksum):
        """Добавляем запись в таблицу dle_files"""
        try:
            cursor = self.connection.cursor()

            # Генерируем уникальное имя файла на сервере
            timestamp = str(int(time.time()))
            server_filename = f"{timestamp[:8]}_{filename}"

            # Относительный путь для базы данных
            relative_path = f"{self.download_dir.name}/{server_filename}"

            insert_query = """
            INSERT INTO dle_files (news_id, name, onserver, author, date, dcount, size, checksum, driver, is_public)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                news_id,
                filename,
                relative_path,
                'app4ok',
                timestamp,
                0,
                file_size,
                checksum,
                2,
                0
            )

            cursor.execute(insert_query, values)
            file_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()

            print(f"✅ Файл добавлен в dle_files с ID: {file_id}")
            return file_id

        except Error as e:
            print(f"❌ Ошибка добавления в dle_files: {e}")
            return None

    def update_dle_post(self, news_id, file_id, original_filename):
        """Обновляем поле apk-original в таблице dle_post"""
        try:
            cursor = self.connection.cursor()

            # Получаем текущие xfields
            select_query = "SELECT xfields FROM dle_post WHERE id = %s"
            cursor.execute(select_query, (news_id,))
            result = cursor.fetchone()

            if not result:
                print(f"❌ Новость с ID {news_id} не найдена")
                return False

            xfields = result[0]

            # Форматируем имя файла для attachment
            formatted_filename = self.format_filename_for_attachment(original_filename)

            # Обновляем поле apk-original
            new_attachment = f"[attachment={file_id}:{formatted_filename}]"

            # Ищем и заменяем существующее поле apk-original
            pattern = r'apk-original\|[^|]*\|\|'
            replacement = f'apk-original|{new_attachment}||'

            if re.search(pattern, xfields):
                new_xfields = re.sub(pattern, replacement, xfields)
            else:
                # Если поля нет, добавляем в конец
                new_xfields = xfields + f'||apk-original|{new_attachment}||'

            # Обновляем запись
            update_query = "UPDATE dle_post SET xfields = %s WHERE id = %s"
            cursor.execute(update_query, (new_xfields, news_id))
            self.connection.commit()
            cursor.close()

            print(f"✅ Обновлено поле apk-original для новости {news_id}: {new_attachment}")
            return True

        except Error as e:
            print(f"❌ Ошибка обновления dle_post: {e}")
            return False

    def add_to_tracking(self, news_id, app_name, version, file_size, file_path, checksum, source_url):
        """Добавляем запись в таблицу отслеживания"""
        try:
            cursor = self.connection.cursor()

            insert_query = """
            INSERT INTO file_tracking (news_id, app_name, version, file_size, file_path, checksum, source_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            values = (news_id, app_name, version, file_size, str(file_path), checksum, source_url)

            cursor.execute(insert_query, values)
            self.connection.commit()
            cursor.close()

            print(f"✅ Добавлена запись в таблицу отслеживания")
            return True

        except Error as e:
            print(f"❌ Ошибка добавления в tracking: {e}")
            return False

    async def process_single_link(self, link_data):
        """Обрабатываем одну ссылку"""
        print(f"\n🔄 Обрабатываем: {link_data['filename']} (ID: {link_data['news_id']})")

        # Извлекаем информацию о приложении ДО нормализации
        app_name = self.extract_app_name_from_filename(link_data['filename'])
        expected_version = self.extract_version_from_filename(link_data['filename'])

        print(f"📱 Приложение: {app_name}")
        print(f"🔢 Ожидаемая версия: {expected_version}")

        # Проверяем нужно ли обновление
        need_update, existing_data = self.check_if_update_needed(
            link_data['news_id'], app_name, expected_version
        )

        if not need_update:
            print("⏭️ Пропускаем, версия актуальна")
            return True

        # Скачиваем файл
        try:
            downloaded_file, actual_version = await self.download_from_apkcombo(link_data['url'])

            if not downloaded_file:
                print("❌ Не удалось скачать файл")
                return False

            # Получаем информацию о файле
            file_size = downloaded_file.stat().st_size
            checksum = self.calculate_checksum(downloaded_file)

            print(f"📊 Размер файла: {file_size} байт")
            print(f"🔐 Чексумма: {checksum}")

            # Добавляем в dle_files
            file_id = self.add_to_dle_files(
                link_data['news_id'],
                downloaded_file.name,
                str(downloaded_file),
                file_size,
                checksum
            )

            if not file_id:
                print("❌ Не удалось добавить файл в dle_files")
                return False

            # Обновляем dle_post с исходным именем файла (до нормализации)
            success = self.update_dle_post(
                link_data['news_id'],
                file_id,
                link_data['filename']  # Используем исходное имя файла
            )

            if not success:
                print("❌ Не удалось обновить dle_post")
                return False

            # Добавляем в таблицу отслеживания с версией ДО нормализации
            self.add_to_tracking(
                link_data['news_id'],
                app_name,
                expected_version,  # Используем версию ДО нормализации
                file_size,
                downloaded_file,
                checksum,
                link_data['url']
            )

            print(f"✅ Файл {downloaded_file.name} успешно обработан!")
            return True

        except Exception as e:
            print(f"❌ Ошибка обработки файла: {e}")
            return False

    async def process_links_file(self):
        """Обрабатываем файл со ссылками"""
        if not os.path.exists(LINKS_FILE):
            print(f"❌ Файл {LINKS_FILE} не найден")
            return

        print(f"📄 Читаем файл: {LINKS_FILE}")

        with open(LINKS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        print(f"📊 Найдено {len(lines)} строк")

        processed = 0
        errors = 0

        for i, line in enumerate(lines, 1):
            print(f"\n{'='*50}")
            print(f"📝 Строка {i}/{len(lines)}")

            link_data = self.parse_link_line(line)
            if not link_data:
                print(f"⚠️ Не удалось распарсить строку: {line.strip()}")
                continue

            # Проверяем что это apkcombo ссылка
            if 'apkcombo.com' not in link_data['url']:
                print(f"⏭️ Пропускаем не-apkcombo ссылку: {link_data['url']}")
                continue

            try:
                success = await self.process_single_link(link_data)
                if success:
                    processed += 1
                else:
                    errors += 1

            except Exception as e:
                print(f"❌ Критическая ошибка обработки строки {i}: {e}")
                errors += 1
                continue

        print(f"\n{'='*50}")
        print(f"📊 ИТОГИ:")
        print(f"✅ Успешно обработано: {processed}")
        print(f"❌ Ошибок: {errors}")
        print(f"📄 Всего строк: {len(lines)}")

async def main():
    """Главная функция"""
    print("🚀 Запуск системы обработки файлов")

    processor = FileProcessor()

    # Подключаемся к базе данных
    if not processor.connect_db():
        print("❌ Не удалось подключиться к базе данных")
        return

    try:
        # Обрабатываем файл со ссылками
        await processor.process_links_file()

    finally:
        # Отключаемся от базы данных
        processor.disconnect_db()

    print("🏁 Обработка завершена")

if __name__ == "__main__":
    asyncio.run(main())
