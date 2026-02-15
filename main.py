# main.py - ГЛАВНЫЙ ФАЙЛ ЗАПУСКА
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    try:
        from handlers import bot
        
        logger.info("=" * 50)
        logger.info("Запуск CipherBot v1.0")
        logger.info("=" * 50)
        logger.info("Бот успешно запущен!")
        
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except ImportError as e:
        logger.error(f"Ошибка импорта: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
