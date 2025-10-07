# Система обработки файлов APK/XAPK

Автоматическая система для скачивания и обновления APK/XAPK файлов с сайта apkcombo.com с интеграцией в CMS DataLife Engine.

## 🚀 Возможности

- ✅ Парсинг файла `step4_links.txt` со ссылками на приложения
- ✅ Автоматическое скачивание файлов с apkcombo.com через Playwright
- ✅ Отслеживание версий приложений и автоматическое обновление
- ✅ Интеграция с базой данных DataLife Engine
- ✅ Обход защиты Cloudflare
- ✅ Автоматическое создание папок по месяцам (формат: год-месяц)
- ✅ Вычисление MD5 чексумм файлов
- ✅ Обновление записей в таблицах `dle_files` и `dle_post`

## 📋 Требования

- Python 3.8+
- MySQL/MariaDB
- Playwright
- mysql-connector-python

## 🛠️ Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository_url>
cd <repository_name>
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Установите браузеры для Playwright:**
```bash
playwright install chromium
```

4. **Настройте базу данных:**
```bash
mysql -u your_user -p your_database < setup_database.sql
```

5. **Создайте конфигурационный файл:**
```bash
cp config_example.py config.py
# Отредактируйте config.py с вашими настройками
```

## ⚙️ Конфигурация

Отредактируйте файл `config.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'your_database_name',
    'user': 'your_username', 
    'password': 'your_password'
}
```

## 📁 Структура файлов

```
├── step5_file_processor.py    # Основной скрипт
├── config_example.py          # Пример конфигурации
├── setup_database.sql         # SQL для создания таблиц
├── requirements.txt           # Зависимости Python
├── step4_links_example.txt    # Пример файла со ссылками
└── README.md                  # Документация
```

## 📄 Формат файла step4_links.txt

```
news_id,[attachment=old_file_id:filename],apkcombo_url
```

Пример:
```
1,[attachment=861:Apple Music_5.0.0.xapk],https://apkcombo.com/ru/apple-music/com.apple.android.music/
2,[attachment=862:WhatsApp_2.23.25.xapk],https://apkcombo.com/ru/whatsapp/com.whatsapp/
```

## 🗄️ Структура базы данных

### Таблица file_tracking (создается автоматически)
```sql
CREATE TABLE file_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    news_id INT NOT NULL,
    app_name VARCHAR(255) NOT NULL,
    version VARCHAR(100) NOT NULL,
    file_size BIGINT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    checksum VARCHAR(32) NOT NULL,
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    source_url VARCHAR(500) NOT NULL
);
```

### Интеграция с DataLife Engine
Система автоматически:
- Добавляет записи в таблицу `dle_files`
- Обновляет поле `apk-original` в таблице `dle_post`

## 🚀 Запуск

```bash
python step5_file_processor.py
```

## 📊 Логика работы

1. **Чтение файла:** Парсинг `step4_links.txt`
2. **Проверка версий:** Сравнение с данными в `file_tracking`
3. **Скачивание:** Если версия изменилась - скачивание нового файла
4. **Сохранение:** Файлы сохраняются в `/www/n2.anplus1.com/files/YYYY-MM/`
5. **База данных:** Обновление таблиц `dle_files`, `dle_post`, `file_tracking`

## 🔄 Автоматическое обновление

Система отслеживает версии приложений:
- При первом запуске скачивает все файлы
- При повторных запусках проверяет версии
- Обновляет только изменившиеся файлы

## 📝 Логирование

Система выводит подробные логи:
- ✅ Успешные операции
- ❌ Ошибки и исключения  
- 🔄 Процесс выполнения
- 📊 Статистика обработки

## 🛡️ Обработка ошибок

- Автоматический обход Cloudflare
- Повторные попытки при сбоях
- Детальное логирование ошибок
- Сохранение скриншотов для отладки

## 📈 Мониторинг

Для мониторинга используйте SQL запросы:

```sql
-- Последние обновления
SELECT * FROM file_tracking ORDER BY last_updated DESC LIMIT 10;

-- Статистика по приложениям
SELECT app_name, COUNT(*) as updates_count 
FROM file_tracking 
GROUP BY app_name;

-- Файлы за текущий месяц
SELECT * FROM file_tracking 
WHERE download_date >= DATE_FORMAT(NOW(), '%Y-%m-01');
```

## 🔧 Устранение неполадок

### Ошибки подключения к БД
- Проверьте настройки в `config.py`
- Убедитесь что MySQL сервер запущен
- Проверьте права пользователя

### Ошибки скачивания
- Проверьте доступность apkcombo.com
- Убедитесь что Playwright установлен корректно
- Проверьте права на запись в папку загрузок

### Ошибки Cloudflare
- Система автоматически ожидает прохождения проверки
- При необходимости увеличьте `cloudflare_wait` в конфигурации

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи выполнения
2. Убедитесь в корректности конфигурации
3. Проверьте доступность внешних ресурсов
4. Изучите сохраненные скриншоты отладки

