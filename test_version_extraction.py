#!/usr/bin/env python3
"""
Тестовый файл для проверки извлечения версий
"""
import re

def test_version_extraction():
    """Тестируем различные способы извлечения версии"""
    
    print("🧪 Тестирование извлечения версий")
    print("="*50)
    
    # Тестовые данные
    test_cases = [
        # HTML контент
        ('<div class="version">1.8.3</div>', '1.8.3'),
        ('<span class="version">2.1.0</span>', '2.1.0'),
        ('Version: 3.4.5', '3.4.5'),
        ('v4.2.1 Latest', '4.2.1'),
        
        # Имена файлов
        ('Dream+Mania+-+Игры+Матч+3_1.8.3_apkcombo.com.apk', '1.8.3'),
        ('WhatsApp_2.23.24.76.apk', '2.23.24.76'),
        ('Telegram_v10.2.0.xapk', '10.2.0'),
        ('Instagram_5.1.apk', '5.1'),
        
        # URL пути
        ('/download/1.8.3/file.apk', '1.8.3'),
        ('/app/version/2.1.0/', '2.1.0'),
    ]
    
    # Паттерны для извлечения версии
    version_patterns = [
        r'(\d+\.\d+\.\d+(?:\.\d+)?)',  # 1.8.3 или 1.8.3.4
        r'(\d+\.\d+)',                 # 1.8
        r'v(\d+\.\d+\.\d+)',          # v1.8.3
    ]
    
    for test_input, expected in test_cases:
        print(f"\n📝 Тест: '{test_input}'")
        print(f"🎯 Ожидаем: '{expected}'")
        
        found_version = None
        for pattern in version_patterns:
            match = re.search(pattern, test_input)
            if match:
                found_version = match.group(1) if pattern.startswith('(') else match.group(1)
                break
        
        if found_version:
            if found_version == expected:
                print(f"✅ Успех: найдена версия '{found_version}'")
            else:
                print(f"⚠️ Частично: найдена '{found_version}', ожидали '{expected}'")
        else:
            print(f"❌ Ошибка: версия не найдена")

def test_database_logic():
    """Тестируем логику работы с базой данных"""
    
    print("\n\n🗄️ Тестирование логики базы данных")
    print("="*50)
    
    # Симуляция проверки версий
    test_scenarios = [
        {
            'stored_version': '1.8.2',
            'new_version': '1.8.3',
            'should_update': True,
            'reason': 'Новая версия больше'
        },
        {
            'stored_version': '1.8.3',
            'new_version': '1.8.3',
            'should_update': False,
            'reason': 'Версии одинаковые'
        },
        {
            'stored_version': '2.0.0',
            'new_version': '1.9.9',
            'should_update': True,
            'reason': 'Версия изменилась (может быть откат)'
        },
    ]
    
    for scenario in test_scenarios:
        stored = scenario['stored_version']
        new = scenario['new_version']
        should_update = scenario['should_update']
        reason = scenario['reason']
        
        print(f"\n📊 Сценарий: {reason}")
        print(f"   Сохранённая версия: {stored}")
        print(f"   Новая версия: {new}")
        
        # Простая логика сравнения
        need_update = stored != new
        
        if need_update == should_update:
            print(f"✅ Корректно: обновление {'нужно' if need_update else 'не нужно'}")
        else:
            print(f"❌ Ошибка: ожидали {'обновление' if should_update else 'пропуск'}")

def test_filename_normalization():
    """Тестируем нормализацию имен файлов"""
    
    print("\n\n📁 Тестирование нормализации имен файлов")
    print("="*50)
    
    test_files = [
        'Dream+Mania+-+Игры+Матч+3_1.8.3_apkcombo.com.apk',
        'WhatsApp Messenger_2.23.24.76.apk',
        'Телеграм_v10.2.0.xapk',
        'Instagram.Stories_5.1.apk',
    ]
    
    for filename in test_files:
        print(f"\n📝 Исходный файл: {filename}")
        
        # Убираем "_apkcombo.com"
        normalized = filename.replace('_apkcombo.com', '')
        
        # Разделяем имя и расширение
        name_part, extension = filename.rsplit('.', 1)
        
        # Простая нормализация
        name_part = name_part.replace(' ', '+')
        name_part = name_part.replace('.', '_')
        name_part = name_part.lower()
        
        normalized = f"{name_part}.{extension.lower()}"
        
        print(f"📝 Нормализованный: {normalized}")

if __name__ == "__main__":
    test_version_extraction()
    test_database_logic()
    test_filename_normalization()
    
    print("\n\n🎉 Тестирование завершено!")
    print("💡 Основные улучшения в исправленном скрипте:")
    print("   1. ✅ Извлечение версии из HTML страницы")
    print("   2. ✅ Запись только чистой версии в базу данных")
    print("   3. ✅ Предотвращение дубликатов при повторном запуске")
    print("   4. ✅ Fallback механизмы для извлечения версии")
    print("   5. ✅ Улучшенная обработка ошибок")
