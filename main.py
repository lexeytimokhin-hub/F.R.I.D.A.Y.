#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CipherBot - Бот для создания и использования шифров
Версия: 1.0.0
"""

import sys
import logging
import threading
import time
from flask import Flask

# ========== ЗАГЛУШКА ДЛЯ RENDER (ЧТОБЫ НЕ БЫЛО ОШИБКИ ПОРТА) ==========
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ CipherBot is running! Бот работает!"

@app.route('/health')
def health():
    return "OK", 200

def run_web_server():
    """Запускает веб-сервер на порту 10000 для Render"""
    try:
        app.run(host='0.0.0.0', port=10000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"⚠️ Ошибка запуска веб-сервера: {e}")

# Запускаем веб-сервер в отдельном потоке
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()
print("✅ Веб-сервер для Render запущен на порту 10000")

# ========== НАСТРОЙКА ЛОГИРОВАНИЯ ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ========== ФУНКЦИЯ ПИНГА ДЛЯ ПРОБУЖДЕНИЯ ==========
def ping_self():
    """Пинг самого себя чтобы не засыпать"""
    import requests
    time.sleep(60)  # Ждем минуту пока бот запустится
    
    while True:
        try:
            # Пингуем свой же сервер
            requests.get("http://localhost:10000/health", timeout=5)
            print(f"✅ Самопроверка в {time.strftime('%H:%M:%S')}")
        except:
            print(f"⚠️ Ошибка самопроверки в {time.strftime('%H:%M:%S')}")
        
        # Проверяем каждые 5 минут
        time.sleep(300)

# Запускаем пингер
pinger_thread = threading.Thread(target=ping_self, daemon=True)
pinger_thread.start()
print("✅ Пингер запущен")

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
def main():
    """Главная функция запуска бота"""
    try:
        from handlers import bot
        
        logger.info("=" * 50)
        logger.info("Запуск CipherBot v1.0")
        logger.info("=" * 50)
        logger.info("✅ Бот успешно запущен и готов к работе!")
        logger.info("✅ Веб-сервер работает на порту 10000")
        logger.info("=" * 50)
        
        # Запускаем бота
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта модулей: {e}")
        logger.error("Убедитесь, что установлены все зависимости из requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        logger.error("Бот остановлен")
        sys.exit(1)

if __name__ == '__main__':
    main()
