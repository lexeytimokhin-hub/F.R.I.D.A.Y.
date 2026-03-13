# config.py - КОНФИГУРАЦИЯ БОТА
import os

# Токен бота (получи у @BotFather)
TOKEN = os.environ.get('TOKEN', 'YOUR_BOT_TOKEN_HERE')
DB_NAME = 'ciphers.db'
VERSION = '2.0.0'

# КРАСИВЫЕ ЭМОДЗИ ДЛЯ ИНТЕРФЕЙСА
EMOJIS = {
    # Основные
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'heart': '❤️',
    'star': '⭐',
    'menu': '📋',
    'back': '🔙',
    'next': '➡️',
    'prev': '⬅️',
    
    # Шифрование
    'cipher': '🔐',
    'decipher': '🔓',
    'key': '🔑',
    'search': '🔍',
    'lock': '🔒',
    'unlock': '🔓',
    
    # Действия
    'save': '💾',
    'delete': '🗑️',
    'edit': '✏️',
    'share': '📤',
    'import': '📥',
    'settings': '⚙️',
    'help': '❓',
    'link': '🔗',
    'qr': '📱',
    
    # Базовые шифры (ДОБАВЛЕНО!)
    'caesar': '🔢',
    'atbash': '🪞',
    'vigenere': '🔑',
    'morse': '⚡',
    'keyboard': '⌨️',
    
    # Дополнительные (ДОБАВЛЕНО!)
    'magic': '🔮',
    'crown': '👑',
    'zap': '⚡',
    'gold': '🥇',
    'silver': '🥈',
    'bronze': '🥉',
    'medal': '🏅',
    'time': '⏰',
    'stats': '📊',
    'users': '👥',
    'fire': '🔥',
    'sparkles': '✨',
    'trophy': '🏆',
    'rainbow': '🌈',
}
