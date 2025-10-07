# 🚀 Быстрая установка зависимостей

## Проблема
```
ModuleNotFoundError: No module named 'mysql'
```

## ✅ Решение

### Вариант 1: Автоматическая установка
```bash
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### Вариант 2: Ручная установка
```bash
# Устанавливаем зависимости Python
pip3 install playwright==1.40.0
pip3 install mysql-connector-python==8.2.0

# Устанавливаем браузеры для Playwright
python3 -m playwright install chromium
```

### Вариант 3: Через requirements.txt
```bash
pip3 install -r requirements.txt
python3 -m playwright install chromium
```

## 📋 Настройка конфигурации

1. **Создайте конфигурационный файл:**
```bash
cp config_example.py config.py
```

2. **Отредактируйте config.py:**
```python
DB_CONFIG = {
    'host': 'localhost',
    'database': 'your_real_database_name',
    'user': 'your_real_username', 
    'password': 'your_real_password'
}
```

3. **Создайте таблицы в базе данных:**
```bash
mysql -u your_username -p your_database < setup_database.sql
```

## 🚀 Запуск

```bash
python3 step5_file_processor.py
```

## ✅ Проверка установки

```bash
python3 -c "import mysql.connector; print('MySQL connector OK')"
python3 -c "import playwright; print('Playwright OK')"
```

## 📝 Примечания

- Скрипт теперь автоматически ищет файл `config.py`
- Если `config.py` не найден, используются настройки по умолчанию
- Обязательно создайте и настройте `config.py` перед запуском

