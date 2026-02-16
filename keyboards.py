# keyboards.py - ПОЛНАЯ ВЕРСИЯ С КНОПКОЙ МОРЗЕ
from telebot import types
from config import EMOJIS

def get_main_keyboard():
    """Главная клавиатура"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    buttons = [
        types.KeyboardButton(f"{EMOJIS['cipher']} Зашифровать"),
        types.KeyboardButton(f"{EMOJIS['decipher']} Расшифровать"),
        types.KeyboardButton(f"{EMOJIS['key']} Мои шифры"),
        types.KeyboardButton(f"📋 Базовые шифры"),
        types.KeyboardButton(f"⌨️ Раскладка"),
        types.KeyboardButton(f"⚡ Морзе"),  # НОВАЯ КНОПКА!
        types.KeyboardButton(f"{EMOJIS['share']} Поделиться"),
        types.KeyboardButton(f"{EMOJIS['settings']} Настройки"),
        types.KeyboardButton(f"{EMOJIS['help']} Помощь")
    ]
    
    keyboard.add(*buttons)
    return keyboard

def get_ciphers_keyboard(ciphers: list, page: int = 0, items_per_page: int = 5):
    """Клавиатура со списком шифров"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    start = page * items_per_page
    end = start + items_per_page
    page_ciphers = ciphers[start:end]
    
    for cipher in page_ciphers:
        default_mark = "⭐ " if cipher['is_default'] else ""
        btn = types.InlineKeyboardButton(
            f"{default_mark}{cipher['name']}",
            callback_data=f"select_cipher_{cipher['id']}"
        )
        keyboard.add(btn)
    
    # Навигация
    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(
            f"{EMOJIS['prev']} Назад", 
            callback_data=f"ciphers_page_{page-1}"
        ))
    
    if end < len(ciphers):
        nav_buttons.append(types.InlineKeyboardButton(
            f"Вперед {EMOJIS['next']}", 
            callback_data=f"ciphers_page_{page+1}"
        ))
    
    if nav_buttons:
        keyboard.row(*nav_buttons)
    
    # Дополнительные кнопки
    keyboard.row(
        types.InlineKeyboardButton(
            f"{EMOJIS['save']} Новый шифр", 
            callback_data="new_cipher"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['import']} Импорт", 
            callback_data="import_cipher"
        )
    )
    
    keyboard.row(
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} Назад", 
            callback_data="back_to_main"
        )
    )
    
    return keyboard

def get_cipher_actions_keyboard(cipher_id: int, is_default: bool = False):
    """Клавиатура действий с шифром"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        types.InlineKeyboardButton(
            f"{EMOJIS['cipher']} Использовать", 
            callback_data=f"use_cipher_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['share']} Поделиться", 
            callback_data=f"share_cipher_{cipher_id}"
        )
    ]
    
    keyboard.add(*buttons)
    
    buttons2 = [
        types.InlineKeyboardButton(
            f"{EMOJIS['edit']} Переименовать", 
            callback_data=f"rename_cipher_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"🔄 Сменить шифр", 
            callback_data=f"change_cipher_{cipher_id}"
        )
    ]
    
    keyboard.add(*buttons2)
    
    if not is_default:
        keyboard.add(
            types.InlineKeyboardButton(
                f"{EMOJIS['star']} Сделать основным", 
                callback_data=f"set_default_{cipher_id}"
            )
        )
    
    keyboard.row(
        types.InlineKeyboardButton(
            f"{EMOJIS['delete']} Удалить", 
            callback_data=f"delete_cipher_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} К списку", 
            callback_data="back_to_ciphers"
        )
    )
    
    return keyboard

def get_share_options_keyboard(cipher_id: int):
    """Клавиатура с вариантами шаринга"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        types.InlineKeyboardButton(
            f"📝 Ссылка", 
            callback_data=f"share_text_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"📱 QR-код", 
            callback_data=f"share_qr_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"🔢 Код", 
            callback_data=f"share_code_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} Назад", 
            callback_data=f"select_cipher_{cipher_id}"
        )
    ]
    
    keyboard.add(*buttons[:2])
    keyboard.add(*buttons[2:])
    
    return keyboard

def get_new_cipher_keyboard():
    """Клавиатура создания нового шифра"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        types.InlineKeyboardButton("🎲 Случайный", callback_data="random_cipher"),
        types.InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data="back_to_ciphers")
    ]
    
    keyboard.add(*buttons)
    return keyboard

def get_settings_keyboard():
    """Клавиатура настроек"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    buttons = [
        types.InlineKeyboardButton(
            f"{EMOJIS['info']} Статистика", 
            callback_data="show_stats"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} Назад", 
            callback_data="back_to_main"
        )
    ]
    
    keyboard.add(*buttons)
    return keyboard

def get_confirm_keyboard(action: str, cipher_id: int = None):
    """Клавиатура подтверждения"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if cipher_id:
        callback_data = f"confirm_{action}_{cipher_id}"
    else:
        callback_data = f"confirm_{action}"
    
    keyboard.add(
        types.InlineKeyboardButton(f"{EMOJIS['success']} Да", callback_data=callback_data),
        types.InlineKeyboardButton(f"{EMOJIS['error']} Нет", callback_data="cancel")
    )
    
    return keyboard

def get_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(
        f"{EMOJIS['back']} Назад", 
        callback_data="back_to_main"
    ))
    return keyboard
