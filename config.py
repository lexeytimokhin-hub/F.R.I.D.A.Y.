# config.py
import os
TOKEN = os.environ.get('TOKEN', 'YOUR_BOT_TOKEN_HERE')  # Вставьте свой токен
DB_NAME = 'ciphers.db'
VERSION = '1.0.0'

# Эмодзи для интерфейса
EMOJIS = {
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'cipher': '🔐',
    'decipher': '🔓',
    'key': '🔑',
    'settings': '⚙️',
    'info': 'ℹ️',
    'heart': '❤️',
    'star': '⭐',
    'lock': '🔒',
    'unlock': '🔓',
    'save': '💾',
    'delete': '🗑️',
    'edit': '✏️',
    'back': '🔙',
    'next': '➡️',
    'prev': '⬅️',
    'menu': '📋',
    'help': '❓',
    'link': '🔗',
    'share': '📤',
    'import': '📥',
    'qr': '📱'
}

