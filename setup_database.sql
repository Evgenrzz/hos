-- Создание таблицы для отслеживания скачанных файлов
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

-- Пример запроса для проверки обновлений
-- SELECT news_id, app_name, version, file_size, download_date 
-- FROM file_tracking 
-- WHERE news_id = 25 AND app_name = 'Apple Music' 
-- ORDER BY last_updated DESC LIMIT 1;

-- Пример запроса для получения всех файлов приложения
-- SELECT * FROM file_tracking WHERE app_name = 'Apple Music' ORDER BY download_date DESC;

