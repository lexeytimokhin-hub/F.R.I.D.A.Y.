# keyboards.py - КРАСИВОЕ МЕНЮ С ЭМОДЗИ
from telebot import types
from config import EMOJIS

def get_main_keyboard():
    """Главная клавиатура с красивым дизайном"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    # Первый ряд - основные функции
    row1 = [
        types.KeyboardButton(f"{EMOJIS['cipher']} Зашифровать"),
        types.KeyboardButton(f"{EMOJIS['decipher']} Расшифровать"),
    ]
    
    # Второй ряд - управление шифрами
    row2 = [
        types.KeyboardButton(f"{EMOJIS['key']} Мои шифры"),
        types.KeyboardButton(f"{EMOJIS['share']} Поделиться"),
    ]
    
    # Третий ряд - базовые шифры
    row3 = [
        types.KeyboardButton(f"{EMOJIS['caesar']} Цезарь"),
        types.KeyboardButton(f"{EMOJIS['atbash']} Атбаш"),
        types.KeyboardButton(f"{EMOJIS['vigenere']} Виженер"),
    ]
    
    # Четвертый ряд - специальные
    row4 = [
        types.KeyboardButton(f"{EMOJIS['morse']} Морзе"),
        types.KeyboardButton(f"{EMOJIS['keyboard']} Раскладка"),
    ]
    
    # Пятый ряд - настройки и помощь
    row5 = [
        types.KeyboardButton(f"{EMOJIS['settings']} Настройки"),
        types.KeyboardButton(f"{EMOJIS['help']} Помощь"),
    ]
    
    # Добавляем все ряды
    keyboard.row(*row1)
    keyboard.row(*row2)
    keyboard.row(*row3)
    keyboard.row(*row4)
    keyboard.row(*row5)
    
    return keyboard

def get_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{EMOJIS['back']} Назад"))
    return keyboard

def get_cancel_keyboard():
    """Клавиатура с кнопкой отмены"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(f"{EMOJIS['error']} Отмена"))
    return keyboard

def get_ciphers_keyboard(ciphers: list, page: int = 0, items_per_page: int = 5):
    """Красивая клавиатура со списком шифров"""
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    start = page * items_per_page
    end = start + items_per_page
    page_ciphers = ciphers[start:end]
    
    for cipher in page_ciphers:
        # Основной шифр отмечаем короной
        if cipher['is_default']:
            name = f"{EMOJIS['crown']} {cipher['name']} (основной)"
        else:
            name = f"{EMOJIS['key']} {cipher['name']}"
        
        btn = types.InlineKeyboardButton(
            name,
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
    
    # Кнопки действий
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
            f"{EMOJIS['back']} В меню", 
            callback_data="back_to_main"
        )
    )
    
    return keyboard

def get_cipher_actions_keyboard(cipher_id: int, is_default: bool = False):
    """Красивая клавиатура действий с шифром"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    # Основные действия
    actions = [
        types.InlineKeyboardButton(
            f"{EMOJIS['cipher']} Использовать", 
            callback_data=f"use_cipher_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['share']} Поделиться", 
            callback_data=f"share_cipher_{cipher_id}"
        )
    ]
    keyboard.add(*actions)
    
    # Редактирование
    edit_actions = [
        types.InlineKeyboardButton(
            f"{EMOJIS['edit']} Переименовать", 
            callback_data=f"rename_cipher_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"🔄 Сменить шифр", 
            callback_data=f"change_cipher_{cipher_id}"
        )
    ]
    keyboard.add(*edit_actions)
    
    # Дополнительные действия
    if not is_default:
        keyboard.add(
            types.InlineKeyboardButton(
                f"{EMOJIS['star']} Сделать основным", 
                callback_data=f"set_default_{cipher_id}"
            )
        )
    
    # Опасные действия
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
    """Красивая клавиатура для шаринга"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    options = [
        types.InlineKeyboardButton(
            f"{EMOJIS['link']} Ссылка", 
            callback_data=f"share_text_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['qr']} QR-код", 
            callback_data=f"share_qr_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['key']} Код", 
            callback_data=f"share_code_{cipher_id}"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} Назад", 
            callback_data=f"select_cipher_{cipher_id}"
        )
    ]
    
    keyboard.add(*options[:2])
    keyboard.add(*options[2:])
    
    return keyboard

def get_morse_menu_keyboard():
    """Красивое меню для азбуки Морзе"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        types.InlineKeyboardButton(
            f"{EMOJIS['morse']} Текст → Морзе", 
            callback_data="morse_encode"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['magic']} Морзе → Текст", 
            callback_data="morse_decode"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} В меню", 
            callback_data="back_to_main"
        )
    ]
    
    keyboard.add(*buttons[:2])
    keyboard.add(buttons[2])
    
    return keyboard

def get_basic_ciphers_keyboard():
    """Красивое меню для базовых шифров"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    buttons = [
        types.InlineKeyboardButton(
            f"{EMOJIS['caesar']} Цезарь", 
            callback_data="basic_caesar"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['atbash']} Атбаш", 
            callback_data="basic_atbash"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['vigenere']} Виженер", 
            callback_data="basic_vigenere"
        ),
        types.InlineKeyboardButton(
            f"{EMOJIS['back']} В меню", 
            callback_data="back_to_main"
        )
    ]
    
    keyboard.add(*buttons[:2])
    keyboard.add(*buttons[2:])
    
    return keyboard

def get_confirm_keyboard(action: str, cipher_id: int = None):
    """Клавиатура подтверждения действия"""
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

def get_decrypt_results_keyboard(results_count: int):
    """Клавиатура для результатов расшифровки"""
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if results_count > 5:
        keyboard.add(types.InlineKeyboardButton(
            f"{EMOJIS['magic']} Показать все ({results_count})",
            callback_data="show_all_decrypt"
        ))
    
    keyboard.add(types.InlineKeyboardButton(
        f"{EMOJIS['decipher']} Новая расшифровка",
        callback_data="decrypt_again"
    ))
    
    keyboard.add(types.InlineKeyboardButton(
        f"{EMOJIS['back']} В меню",
        callback_data="back_to_main"
    ))
    
    return keyboard
