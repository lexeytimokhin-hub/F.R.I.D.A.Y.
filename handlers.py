# handlers.py - ПОЛНАЯ ВЕРСИЯ С УМНОЙ РАСШИФРОВКОЙ И КРАСИВЫМ ИНТЕРФЕЙСОМ
import telebot
from telebot import types
import time
import re

from config import TOKEN, EMOJIS
from cipher import Cipher
from database import Database
from keyboards import *
from utils import *
from basic_ciphers import BasicCiphers, KeyboardCipher
from morse_cipher import MorseCipher
from emoji_helper import EmojiHelper
from smart_decrypt import SmartDecrypt
from ui_messages import UIMessages

# Добавляем недостающие эмодзи
if 'search' not in EMOJIS:
    EMOJIS['search'] = '🔍'
if 'decipher' not in EMOJIS:
    EMOJIS['decipher'] = '🔓'
if 'cipher' not in EMOJIS:
    EMOJIS['cipher'] = '🔐'
if 'magic' not in EMOJIS:
    EMOJIS['magic'] = '🔮'
if 'crown' not in EMOJIS:
    EMOJIS['crown'] = '👑'
if 'zap' not in EMOJIS:
    EMOJIS['zap'] = '⚡'

bot = telebot.TeleBot(TOKEN)
db = Database()

# Хранилище временных данных
temp_data = {}

# ============================================
# КОМАНДА СТАРТ
# ============================================
@bot.message_handler(commands=['start'])
def cmd_start(message):
    user = message.from_user
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    args = message.text.split()
    if len(args) > 1:
        if args[1].startswith('shared_cipher_'):
            cipher_id = args[1].replace('shared_cipher_', '')
            receive_shared_cipher(message, cipher_id)
            return
    
    bot.send_message(
        user.id, 
        UIMessages.welcome_message(user.first_name or user.username or 'Пользователь'),
        parse_mode='Markdown',
        reply_markup=get_main_keyboard()
    )

# ============================================
# ПОЛУЧЕНИЕ ШИФРА ПО ССЫЛКЕ
# ============================================
def receive_shared_cipher(message, cipher_id):
    user_id = message.from_user.id
    
    try:
        cipher_id = int(cipher_id)
        cipher_data = db.get_cipher_by_id(cipher_id)
        
        if cipher_data:
            temp_data[f"import_{user_id}"] = {
                'cipher_id': cipher_id,
                'cipher_data': cipher_data
            }
            
            cipher = Cipher.from_dict(cipher_data)
            
            share_text = f"""
{EMOJIS['star']} *Вам отправили шифр!*

*Название:* {cipher.name}
*Автор:* {cipher_data.get('owner_name', 'Неизвестно')}

{cipher.get_preview(10)}

Хотите добавить этот шифр себе?
            """
            
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton(f"{EMOJIS['save']} Добавить", callback_data=f"import_cipher_{cipher_id}"),
                types.InlineKeyboardButton(f"{EMOJIS['error']} Отмена", callback_data="cancel_import")
            )
            
            bot.send_message(user_id, share_text, parse_mode='Markdown', reply_markup=keyboard)
        else:
            bot.send_message(user_id, f"{EMOJIS['error']} Шифр не найден или удален")
            
    except Exception as e:
        bot.send_message(user_id, f"{EMOJIS['error']} Ошибка при загрузке шифра")

# ============================================
# ОБРАБОТКА ТЕКСТОВЫХ КНОПОК
# ============================================
@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['cipher']} Зашифровать")
def encrypt_text(message):
    user_id = message.from_user.id
    ciphers = db.get_user_ciphers(user_id)
    
    if not ciphers:
        bot.send_message(
            user_id,
            f"{EMOJIS['warning']} У вас еще нет шифра!\n"
            f"Создайте его в разделе 'Мои шифры'.",
            reply_markup=get_back_keyboard()
        )
        return
    
    default_cipher = next((c for c in ciphers if c['is_default']), ciphers[0])
    
    temp_data[f"encrypt_{user_id}"] = {
        'cipher_id': default_cipher['id'],
        'step': 'waiting_text'
    }
    
    cipher = Cipher.from_dict(default_cipher['data'])
    
    bot.send_message(
        user_id,
        f"{EMOJIS['cipher']} *Шифрование*\n\n"
        f"Используется шифр: *{cipher.name}*\n"
        f"{cipher.get_preview(5)}\n\n"
        f"Отправьте текст для шифрования:",
        parse_mode='Markdown',
        reply_markup=get_back_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['decipher']} Расшифровать")
def decrypt_text(message):
    user_id = message.from_user.id
    
    temp_data[f"decrypt_{user_id}"] = {
        'step': 'waiting_text'
    }
    
    bot.send_message(
        user_id,
        UIMessages.smart_decrypt_intro(),
        parse_mode='Markdown',
        reply_markup=get_back_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['key']} Мои шифры")
def show_ciphers(message):
    user_id = message.from_user.id
    ciphers = db.get_user_ciphers(user_id)
    
    if not ciphers:
        cipher = Cipher("Мой первый шифр")
        cipher.generate_random("russian")
        cipher_id = db.save_cipher(user_id, cipher, is_default=True)
        
        bot.send_message(
            user_id,
            UIMessages.cipher_created(cipher.name, cipher.get_preview()),
            parse_mode='Markdown'
        )
        
        ciphers = db.get_user_ciphers(user_id)
    
    text = f"{EMOJIS['key']} *Ваши шифры:*\n\n"
    bot.send_message(
        user_id,
        text,
        parse_mode='Markdown',
        reply_markup=get_ciphers_keyboard(ciphers)
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['caesar']} Цезарь")
def caesar_menu(message):
    user_id = message.from_user.id
    
    temp_data[f"basic_{user_id}"] = {
        'type': 'caesar',
        'step': 'waiting_text'
    }
    
    bot.send_message(
        user_id,
        f"{EMOJIS['caesar']} *Шифр Цезаря*\n\n"
        f"Отправьте текст для шифрования (сдвиг 3):\n\n"
        f"Пример: 'привет' → 'тузжёх'",
        parse_mode='Markdown',
        reply_markup=get_cancel_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['atbash']} Атбаш")
def atbash_menu(message):
    user_id = message.from_user.id
    
    temp_data[f"basic_{user_id}"] = {
        'type': 'atbash',
        'step': 'waiting_text'
    }
    
    bot.send_message(
        user_id,
        f"{EMOJIS['atbash']} *Шифр Атбаш*\n\n"
        f"Отправьте текст для шифрования (зеркальный):\n\n"
        f"Пример: 'привет' → 'крсэъм'",
        parse_mode='Markdown',
        reply_markup=get_cancel_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['vigenere']} Виженер")
def vigenere_menu(message):
    user_id = message.from_user.id
    
    temp_data[f"basic_{user_id}"] = {
        'type': 'vigenere',
        'step': 'waiting_key'
    }
    
    bot.send_message(
        user_id,
        f"{EMOJIS['vigenere']} *Шифр Виженера*\n\n"
        f"Введите ключевое слово:",
        parse_mode='Markdown',
        reply_markup=get_cancel_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['morse']} Морзе")
def morse_menu(message):
    user_id = message.from_user.id
    
    bot.send_message(
        user_id,
        f"{EMOJIS['morse']} *Азбука Морзе*\n\n"
        f"Выберите действие:",
        parse_mode='Markdown',
        reply_markup=get_morse_menu_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['keyboard']} Раскладка")
def keyboard_menu(message):
    user_id = message.from_user.id
    
    temp_data[f"keyboard_{user_id}"] = {
        'step': 'waiting_text'
    }
    
    bot.send_message(
        user_id,
        f"{EMOJIS['keyboard']} *Шифр раскладки клавиатуры*\n\n"
        f"Отправьте текст, и я сменю раскладку:\n"
        f"• Русский → Английский (пример: 'привет' → 'ghbdtn')\n"
        f"• Английский → Русский (пример: 'ghbdtn' → 'привет')\n\n"
        f"Просто отправьте любой текст!",
        parse_mode='Markdown',
        reply_markup=get_cancel_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['share']} Поделиться")
def share_cipher_menu(message):
    user_id = message.from_user.id
    ciphers = db.get_user_ciphers(user_id)
    
    if not ciphers:
        bot.send_message(
            user_id,
            f"{EMOJIS['warning']} У вас нет шифров для публикации!",
            reply_markup=get_back_keyboard()
        )
        return
    
    text = f"{EMOJIS['share']} *Выберите шифр для публикации:*\n\n"
    bot.send_message(
        user_id,
        text,
        parse_mode='Markdown',
        reply_markup=get_ciphers_keyboard(ciphers)
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['settings']} Настройки")
def show_settings(message):
    user_id = message.from_user.id
    ciphers = db.get_user_ciphers(user_id)
    history = db.get_history(user_id, limit=1)
    
    bot.send_message(
        user_id,
        UIMessages.stats_message(
            len(ciphers), 
            len(db.get_history(user_id, limit=1000)),
            format_time(history[0]['created_at']) if history else None
        ),
        parse_mode='Markdown',
        reply_markup=get_settings_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['help']} Помощь")
def show_help(message):
    bot.send_message(
        message.from_user.id,
        UIMessages.help_message(),
        parse_mode='Markdown',
        reply_markup=get_back_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['back']} Назад")
def go_back(message):
    user_id = message.from_user.id
    
    # Очищаем все временные данные для пользователя
    keys_to_delete = []
    for key in temp_data:
        if key.endswith(str(user_id)):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del temp_data[key]
    
    bot.send_message(
        user_id,
        f"{EMOJIS['heart']} Главное меню",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['error']} Отмена")
def cancel_action(message):
    user_id = message.from_user.id
    
    # Очищаем все временные данные для пользователя
    keys_to_delete = []
    for key in temp_data:
        if key.endswith(str(user_id)):
            keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del temp_data[key]
    
    bot.send_message(
        user_id,
        f"{EMOJIS['info']} Действие отменено",
        reply_markup=get_main_keyboard()
    )

# ============================================
# ОБРАБОТКА НАЖАТИЙ НА КНОПКИ
# ============================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    # ===== НАВИГАЦИЯ =====
    if data == "back_to_main":
        bot.edit_message_text(
            f"{EMOJIS['heart']} Главное меню",
            user_id,
            call.message.message_id,
            reply_markup=None
        )
        bot.send_message(
            user_id,
            "Выберите действие:",
            reply_markup=get_main_keyboard()
        )
        return
    
    if data == "back_to_ciphers":
        ciphers = db.get_user_ciphers(user_id)
        bot.edit_message_text(
            f"{EMOJIS['key']} *Ваши шифры:*",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_ciphers_keyboard(ciphers)
        )
        return
    
    # ===== ПАГИНАЦИЯ =====
    if data.startswith("ciphers_page_"):
        page = int(data.split("_")[2])
        ciphers = db.get_user_ciphers(user_id)
        bot.edit_message_reply_markup(
            user_id,
            call.message.message_id,
            reply_markup=get_ciphers_keyboard(ciphers, page)
        )
        return
    
    # ===== СОЗДАНИЕ НОВОГО ШИФРА =====
    if data == "new_cipher":
        bot.edit_message_text(
            f"{EMOJIS['save']} *Создание нового шифра*\n\n"
            f"Выберите тип:",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_new_cipher_keyboard()
        )
        return
    
    # ===== ТИПЫ ШИФРОВ =====
    if data == "random_cipher":
        cipher = Cipher(generate_cipher_name("Случайный шифр"))
        cipher.generate_random("russian")
        cipher_id = db.save_cipher(user_id, cipher)
        
        bot.edit_message_text(
            UIMessages.cipher_created(cipher.name, cipher.get_preview()),
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_cipher_actions_keyboard(cipher_id)
        )
        return
    
    # ===== ВЫБОР ШИФРА =====
    if data.startswith("select_cipher_"):
        cipher_id = int(data.split("_")[2])
        cipher_data = db.get_cipher(cipher_id)
        cipher = Cipher.from_dict(cipher_data)
        
        ciphers = db.get_user_ciphers(user_id)
        is_default = any(c['id'] == cipher_id and c['is_default'] for c in ciphers)
        
        bot.edit_message_text(
            f"{EMOJIS['key']} *{cipher.name}*\n\n"
            f"{cipher.get_preview(15)}",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_cipher_actions_keyboard(cipher_id, is_default)
        )
        return
    
    # ===== ИСПОЛЬЗОВАНИЕ ШИФРА =====
    if data.startswith("use_cipher_"):
        cipher_id = int(data.split("_")[2])
        cipher_data = db.get_cipher(cipher_id)
        cipher = Cipher.from_dict(cipher_data)
        
        temp_data[f"encrypt_{user_id}"] = {
            'cipher_id': cipher_id,
            'step': 'waiting_text'
        }
        
        bot.edit_message_text(
            f"{EMOJIS['cipher']} *Шифрование*\n\n"
            f"Используется шифр: *{cipher.name}*\n"
            f"Отправьте текст для шифрования:",
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    # ===== ПОДЕЛИТЬСЯ ШИФРОМ =====
    if data.startswith("share_cipher_"):
        cipher_id = int(data.split("_")[2])
        cipher_data = db.get_cipher(cipher_id)
        cipher = Cipher.from_dict(cipher_data)
        
        share_text = f"""
{EMOJIS['star']} *Поделиться шифром*

*{cipher.name}*

Выберите способ отправки:
        """
        
        bot.edit_message_text(
            share_text,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_share_options_keyboard(cipher_id)
        )
        return
    
    # ===== ТЕКСТОВАЯ ССЫЛКА =====
    if data.startswith("share_text_"):
        cipher_id = int(data.split("_")[2])
        
        bot_username = bot.get_me().username
        invite_link = f"https://t.me/{bot_username}?start=shared_cipher_{cipher_id}"
        
        bot.edit_message_text(
            UIMessages.share_cipher(
                Cipher.from_dict(db.get_cipher(cipher_id)).name,
                link=invite_link
            ),
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            f"{EMOJIS['back']} Назад", 
            callback_data=f"share_cipher_{cipher_id}"
        ))
        
        bot.send_message(
            user_id,
            "Вернуться к выбору способа:",
            reply_markup=keyboard
        )
        return
    
    # ===== QR-КОД =====
    if data.startswith("share_qr_"):
        cipher_id = int(data.split("_")[2])
        
        try:
            try:
                import qrcode
                from PIL import Image
                from io import BytesIO
                qr_available = True
            except ImportError:
                qr_available = False
            
            if not qr_available:
                bot.edit_message_text(
                    f"{EMOJIS['warning']} *QR-код временно недоступен*\n\n"
                    f"Для работы QR-кода нужно установить библиотеки:\n\n"
                    f"Добавьте в `requirements.txt`:\n"
                    f"```\n"
                    f"qrcode[pil]==7.4.2\n"
                    f"pillow==10.1.0\n"
                    f"```\n\n"
                    f"И перезапустите бота на Render",
                    user_id,
                    call.message.message_id,
                    parse_mode='Markdown'
                )
                
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                keyboard.add(
                    types.InlineKeyboardButton("📝 Ссылка", callback_data=f"share_text_{cipher_id}"),
                    types.InlineKeyboardButton("🔢 Код", callback_data=f"share_code_{cipher_id}"),
                    types.InlineKeyboardButton(f"{EMOJIS['back']} Назад", callback_data=f"share_cipher_{cipher_id}")
                )
                
                bot.send_message(
                    user_id,
                    "Выберите другой способ:",
                    reply_markup=keyboard
                )
                return
            
            cipher_data = db.get_cipher(cipher_id)
            if not cipher_data:
                bot.answer_callback_query(call.id, f"{EMOJIS['error']} Шифр не найден")
                return
            
            cipher = Cipher.from_dict(cipher_data)
            
            bot_username = bot.get_me().username
            invite_link = f"https://t.me/{bot_username}?start=shared_cipher_{cipher_id}"
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(invite_link)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            bio = BytesIO()
            bio.name = 'qr_code.png'
            img.save(bio, 'PNG')
            bio.seek(0)
            
            bot.send_photo(
                user_id,
                photo=bio,
                caption=UIMessages.share_cipher(cipher.name, link=invite_link),
                parse_mode='Markdown'
            )
            
            bot.delete_message(user_id, call.message.message_id)
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                f"{EMOJIS['back']} К шифру", 
                callback_data=f"select_cipher_{cipher_id}"
            ))
            
            bot.send_message(
                user_id,
                "Вернуться к шифру:",
                reply_markup=keyboard
            )
            
        except Exception as e:
            bot.answer_callback_query(
                call.id, 
                f"{EMOJIS['error']} Ошибка: {str(e)[:20]}..."
            )
        return
    
    # ===== КОД ДЛЯ ИМПОРТА =====
    if data.startswith("share_code_"):
        cipher_id = int(data.split("_")[2])
        cipher_data = db.get_cipher(cipher_id)
        
        if not cipher_data:
            bot.answer_callback_query(call.id, f"{EMOJIS['error']} Шифр не найден")
            return
            
        cipher = Cipher.from_dict(cipher_data)
        
        try:
            import_code = cipher.export_to_string()
            
            bot.edit_message_text(
                UIMessages.share_cipher(cipher.name, code=import_code),
                user_id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(
                f"{EMOJIS['back']} Назад", 
                callback_data=f"share_cipher_{cipher_id}"
            ))
            
            bot.send_message(
                user_id,
                "Вернуться к выбору:",
                reply_markup=keyboard
            )
            
        except Exception as e:
            bot.answer_callback_query(
                call.id, 
                f"{EMOJIS['error']} Ошибка"
            )
        return
    
    # ===== ИМПОРТ ШИФРА =====
    if data == "import_cipher":
        temp_data[f"import_waiting_{user_id}"] = True
        
        bot.edit_message_text(
            f"{EMOJIS['import']} *ИМПОРТ ШИФРА*\n\n"
            f"Отправьте код шифра, который вам дали:",
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    # ===== ПОДТВЕРЖДЕНИЕ ИМПОРТА ПО ССЫЛКЕ =====
    if data.startswith("import_cipher_"):
        cipher_id = int(data.split("_")[2])
        
        if f"import_{user_id}" in temp_data:
            cipher_data = temp_data[f"import_{user_id}"]['cipher_data']
            
            cipher = Cipher.from_dict(cipher_data)
            cipher.name = f"{cipher.name} (копия)"
            
            new_id = db.save_cipher(user_id, cipher)
            
            bot.edit_message_text(
                UIMessages.cipher_created(cipher.name, cipher.get_preview()),
                user_id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
            del temp_data[f"import_{user_id}"]
        return
    
    # ===== ОТМЕНА ИМПОРТА =====
    if data == "cancel_import":
        if f"import_{user_id}" in temp_data:
            del temp_data[f"import_{user_id}"]
        
        bot.edit_message_text(
            f"{EMOJIS['info']} Импорт отменен",
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    # ===== ПЕРЕИМЕНОВАНИЕ ШИФРА =====
    if data.startswith("rename_cipher_"):
        cipher_id = int(data.split("_")[2])
        
        temp_data[f"rename_{user_id}"] = {
            'cipher_id': cipher_id
        }
        
        bot.edit_message_text(
            f"{EMOJIS['edit']} *Переименование шифра*\n\n"
            f"Введите новое название для шифра:",
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    # ===== СМЕНА ШИФРА =====
    if data.startswith("change_cipher_"):
        cipher_id = int(data.split("_")[2])
        cipher_data = db.get_cipher(cipher_id)
        cipher = Cipher.from_dict(cipher_data)
        
        temp_data[f"changing_{user_id}"] = {
            'cipher_id': cipher_id,
            'current_letter_index': 0,
            'new_map': {},
            'cipher': cipher
        }
        
        russian_letters = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
        first_letter = russian_letters[0]
        current_symbol = cipher.cipher_map.get(first_letter, "?")
        
        change_text = f"""
{EMOJIS['edit']} *Смена шифра*

*Буква 1/33:* **{first_letter}**
Текущий символ: {current_symbol}

Отправьте новый символ для этой буквы
        """
        
        bot.edit_message_text(
            change_text,
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    # ===== УСТАНОВКА ОСНОВНОГО =====
    if data.startswith("set_default_"):
        cipher_id = int(data.split("_")[2])
        
        if db.set_default_cipher(user_id, cipher_id):
            bot.answer_callback_query(
                call.id,
                f"{EMOJIS['success']} Шифр установлен как основной!"
            )
            
            ciphers = db.get_user_ciphers(user_id)
            cipher_data = db.get_cipher(cipher_id)
            cipher = Cipher.from_dict(cipher_data)
            
            bot.edit_message_text(
                f"{EMOJIS['key']} *{cipher.name} (основной)*\n\n"
                f"{cipher.get_preview(15)}",
                user_id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_cipher_actions_keyboard(cipher_id, True)
            )
        else:
            bot.answer_callback_query(call.id, f"{EMOJIS['error']} Ошибка!")
        return
    
    # ===== УДАЛЕНИЕ =====
    if data.startswith("delete_cipher_"):
        cipher_id = int(data.split("_")[2])
        
        bot.edit_message_text(
            f"{EMOJIS['warning']} *Подтверждение*\n\n"
            f"Вы уверены, что хотите удалить этот шифр?",
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_confirm_keyboard("delete", cipher_id)
        )
        return
    
    # ===== ПОДТВЕРЖДЕНИЕ УДАЛЕНИЯ =====
    if data.startswith("confirm_delete_"):
        cipher_id = int(data.split("_")[2])
        
        if db.delete_cipher(user_id, cipher_id):
            bot.answer_callback_query(call.id, f"{EMOJIS['success']} Шифр удален!")
            
            ciphers = db.get_user_ciphers(user_id)
            bot.edit_message_text(
                f"{EMOJIS['key']} *Ваши шифры:*",
                user_id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=get_ciphers_keyboard(ciphers)
            )
        else:
            bot.answer_callback_query(
                call.id, 
                f"{EMOJIS['error']} Нельзя удалить основной шифр!"
            )
        return
    
    # ===== ОТМЕНА =====
    if data == "cancel":
        bot.edit_message_text(
            f"{EMOJIS['info']} Действие отменено",
            user_id,
            call.message.message_id,
            reply_markup=None
        )
        return
    
    # ===== СТАТИСТИКА =====
    if data == "show_stats":
        ciphers = db.get_user_ciphers(user_id)
        history = db.get_history(user_id, limit=1000)
        
        total_encrypt = sum(1 for h in history if h['operation'] == 'encrypt')
        total_decrypt = sum(1 for h in history if h['operation'] == 'decrypt')
        
        stats_text = f"""
{EMOJIS['info']} *Детальная статистика*

📊 *Шифров:* {len(ciphers)}
📝 *Операций:* {len(history)}
  • Зашифровано: {total_encrypt}
  • Расшифровано: {total_decrypt}

⏰ *Последняя операция:* {format_time(history[0]['created_at']) if history else 'нет'}
        """
        
        bot.edit_message_text(
            stats_text,
            user_id,
            call.message.message_id,
            parse_mode='Markdown',
            reply_markup=get_back_keyboard()
        )
        return
    
    # ===== АЗБУКА МОРЗЕ =====
    if data == "morse_encode":
        temp_data[f"morse_{user_id}"] = {
            'action': 'encode',
            'step': 'waiting_text'
        }
        bot.edit_message_text(
            f"{EMOJIS['morse']} *Текст в Морзе*\n\n"
            f"Отправьте текст для преобразования в сигналы Морзе.\n\n"
            f"Поддерживаются все буквы, цифры и знаки препинания!",
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    if data == "morse_decode":
        temp_data[f"morse_{user_id}"] = {
            'action': 'decode',
            'step': 'waiting_text'
        }
        bot.edit_message_text(
            f"{EMOJIS['morse']} *Морзе в текст*\n\n"
            f"Отправьте сигналы Морзе для расшифровки.\n\n"
            f"Правила записи:\n"
            f"• Точка: `.` или `·`\n"
            f"• Тире: `-` или `_`\n"
            f"• Пробел между буквами: один пробел\n"
            f"• Разделитель слов: `/` или `|`\n\n"
            f"Пример: `.... . .-.. .-.. --- / .-- --- .-. .-.. -..`",
            user_id,
            call.message.message_id,
            parse_mode='Markdown'
        )
        return
    
    # ===== ПОКАЗАТЬ ВСЕ РЕЗУЛЬТАТЫ РАСШИФРОВКИ =====
    if data == "show_all_decrypt":
        if f"decrypt_results_{user_id}" in temp_data:
            results = temp_data[f"decrypt_results_{user_id}"]
            
            bot.edit_message_text(
                UIMessages.decrypt_results(results, show_all=True),
                user_id,
                call.message.message_id,
                parse_mode='Markdown'
            )
            
            keyboard = get_decrypt_results_keyboard(len(results))
            bot.send_message(
                user_id,
                "Что дальше?",
                reply_markup=keyboard
            )
            
            del temp_data[f"decrypt_results_{user_id}"]
        
        return
    
    # ===== ПОВТОРНАЯ РАСШИФРОВКА =====
    if data == "decrypt_again":
        bot.delete_message(user_id, call.message.message_id)
        
        fake_msg = type('obj', (object,), {
            'from_user': type('obj', (object,), {'id': user_id}),
            'chat': type('obj', (object,), {'id': user_id}),
            'text': f"{EMOJIS['decipher']} Расшифровать"
        })
        decrypt_text(fake_msg)
        return

# ============================================
# ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ
# ============================================
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    user_id = message.from_user.id
    text = message.text
    
    # Игнорируем команды и кнопки
    if text.startswith('/') or text in [f"{EMOJIS['cipher']} Зашифровать", 
                                         f"{EMOJIS['decipher']} Расшифровать",
                                         f"{EMOJIS['key']} Мои шифры",
                                         f"{EMOJIS['caesar']} Цезарь",
                                         f"{EMOJIS['atbash']} Атбаш",
                                         f"{EMOJIS['vigenere']} Виженер",
                                         f"{EMOJIS['morse']} Морзе",
                                         f"{EMOJIS['keyboard']} Раскладка",
                                         f"{EMOJIS['share']} Поделиться",
                                         f"{EMOJIS['settings']} Настройки",
                                         f"{EMOJIS['help']} Помощь",
                                         f"{EMOJIS['back']} Назад",
                                         f"{EMOJIS['error']} Отмена"]:
        return
    
    # ===== АЗБУКА МОРЗЕ =====
    if f"morse_{user_id}" in temp_data:
        morse_data = temp_data[f"morse_{user_id}"]
        
        if morse_data['action'] == 'encode':
            result = MorseCipher.text_to_morse(text)
            bot.reply_to(
                message,
                f"{EMOJIS['morse']} *Текст в Морзе*\n\n"
                f"Исходный текст:\n`{text}`\n\n"
                f"Результат:\n`{result}`",
                parse_mode='Markdown'
            )
            del temp_data[f"morse_{user_id}"]
            return
        
        elif morse_data['action'] == 'decode':
            result, error = MorseCipher.morse_to_text(text)
            
            if error:
                bot.reply_to(
                    message,
                    f"{EMOJIS['morse']} *Морзе в текст*\n\n"
                    f"Исходный код:\n`{text}`\n\n"
                    f"Результат:\n`{result}`\n\n"
                    f"⚠️ {error}",
                    parse_mode='Markdown'
                )
            else:
                bot.reply_to(
                    message,
                    f"{EMOJIS['morse']} *Морзе в текст*\n\n"
                    f"Исходный код:\n`{text}`\n\n"
                    f"Результат:\n`{result}`",
                    parse_mode='Markdown'
                )
            del temp_data[f"morse_{user_id}"]
            return
    
    # ===== РАСКЛАДКА КЛАВИАТУРЫ =====
    if f"keyboard_{user_id}" in temp_data:
        # Проверяем, русский или английский
        ru_count = 0
        en_count = 0
        for char in text:
            if 'а' <= char.lower() <= 'я' or char == 'ё':
                ru_count += 1
            elif 'a' <= char.lower() <= 'z':
                en_count += 1
        
        if ru_count > en_count:
            result = KeyboardCipher.ru_to_en(text)
            direction = "🇷🇺 → 🇬🇧"
        else:
            result = KeyboardCipher.en_to_ru(text)
            direction = "🇬🇧 → 🇷🇺"
        
        bot.reply_to(
            message,
            f"{EMOJIS['keyboard']} *Результат смены раскладки*\n\n"
            f"{direction}:\n"
            f"`{result}`",
            parse_mode='Markdown'
        )
        del temp_data[f"keyboard_{user_id}"]
        return
    
    # ===== БАЗОВЫЕ ШИФРЫ =====
    if f"basic_{user_id}" in temp_data:
        basic_data = temp_data[f"basic_{user_id}"]
        
        if basic_data['type'] == 'caesar':
            result = BasicCiphers.caesar_encrypt(text)
            bot.reply_to(
                message,
                f"{EMOJIS['caesar']} *Шифр Цезаря (сдвиг 3)*\n\n"
                f"Исходный текст:\n`{text}`\n\n"
                f"Зашифровано:\n`{result}`",
                parse_mode='Markdown'
            )
            del temp_data[f"basic_{user_id}"]
            return
        
        elif basic_data['type'] == 'atbash':
            result = BasicCiphers.atbash_encrypt(text)
            bot.reply_to(
                message,
                f"{EMOJIS['atbash']} *Шифр Атбаш*\n\n"
                f"Исходный текст:\n`{text}`\n\n"
                f"Зашифровано:\n`{result}`",
                parse_mode='Markdown'
            )
            del temp_data[f"basic_{user_id}"]
            return
        
        elif basic_data['type'] == 'vigenere':
            if basic_data.get('step') == 'waiting_key':
                basic_data['key'] = text
                basic_data['step'] = 'waiting_text'
                bot.reply_to(
                    message,
                    f"{EMOJIS['vigenere']} Ключ *{text}* сохранен.\n\n"
                    f"Теперь отправьте текст для шифрования:",
                    parse_mode='Markdown'
                )
                return
            elif basic_data.get('step') == 'waiting_text':
                key = basic_data.get('key', 'ключ')
                result = BasicCiphers.vigenere_encrypt(text, key)
                bot.reply_to(
                    message,
                    f"{EMOJIS['vigenere']} *Шифр Виженера*\n\n"
                    f"Ключ: `{key}`\n"
                    f"Исходный текст:\n`{text}`\n\n"
                    f"Зашифровано:\n`{result}`",
                    parse_mode='Markdown'
                )
                del temp_data[f"basic_{user_id}"]
                return
    
    # ===== ИМПОРТ ШИФРА =====
    if f"import_waiting_{user_id}" in temp_data:
        try:
            cipher = Cipher.import_from_string(text)
            
            if cipher:
                cipher.name = f"Импортированный: {cipher.name}"
                cipher_id = db.save_cipher(user_id, cipher)
                
                bot.reply_to(
                    message,
                    UIMessages.cipher_created(cipher.name, cipher.get_preview()),
                    parse_mode='Markdown'
                )
                
                del temp_data[f"import_waiting_{user_id}"]
            else:
                bot.reply_to(
                    message,
                    f"{EMOJIS['error']} Неверный формат кода шифра"
                )
        except:
            bot.reply_to(
                message,
                f"{EMOJIS['error']} Ошибка при импорте"
            )
        return
    
    # ===== ПЕРЕИМЕНОВАНИЕ =====
    if f"rename_{user_id}" in temp_data:
        cipher_id = temp_data[f"rename_{user_id}"]['cipher_id']
        
        cipher_data = db.get_cipher(cipher_id)
        if not cipher_data:
            bot.reply_to(message, f"{EMOJIS['error']} Шифр не найден")
            del temp_data[f"rename_{user_id}"]
            return
        
        cipher = Cipher.from_dict(cipher_data)
        
        if cipher.rename(text):
            db.save_cipher(user_id, cipher)
            bot.reply_to(
                message, 
                f"{EMOJIS['success']} Шифр переименован в *{cipher.name}*", 
                parse_mode='Markdown'
            )
        else:
            bot.reply_to(message, f"{EMOJIS['error']} Ошибка переименования")
        
        del temp_data[f"rename_{user_id}"]
        return
    
    # ===== СМЕНА ШИФРА =====
    if f"changing_{user_id}" in temp_data:
        change_data = temp_data[f"changing_{user_id}"]
        current_index = change_data['current_letter_index']
        cipher = change_data['cipher']
        new_map = change_data['new_map']
        
        russian_letters = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
        
        if not text:
            bot.reply_to(message, "Отправьте символ для этой буквы!")
            return
        
        current_letter = russian_letters[current_index]
        new_map[current_letter] = text[0]
        
        next_index = current_index + 1
        
        if next_index < len(russian_letters):
            next_letter = russian_letters[next_index]
            current_symbol = cipher.cipher_map.get(next_letter, "?")
            
            change_data['current_letter_index'] = next_index
            change_data['new_map'] = new_map
            
            change_text = f"""
{EMOJIS['edit']} *Смена шифра*

✅ Буква **{current_letter}** → {text[0]}

*Буква {next_index+1}/33:* **{next_letter}**
Текущий символ: {current_symbol}

Отправьте новый символ
            """
            
            bot.reply_to(message, change_text, parse_mode='Markdown')
            
        else:
            cipher.cipher_map.update(new_map)
            cipher.reverse_map = {v: k for k, v in cipher.cipher_map.items()}
            
            new_cipher_id = db.save_cipher(user_id, cipher)
            db.set_default_cipher(user_id, new_cipher_id)
            
            del temp_data[f"changing_{user_id}"]
            
            finish_text = f"""
{EMOJIS['success']} *Шифр успешно изменен!*

{cipher.get_preview(10)}
            """
            
            bot.reply_to(message, finish_text, parse_mode='Markdown')
            bot.send_message(user_id, "Выберите действие:", reply_markup=get_main_keyboard())
        
        return
    
    # ===== ШИФРОВАНИЕ =====
    if f"encrypt_{user_id}" in temp_data:
        state = temp_data[f"encrypt_{user_id}"]
        
        if state['step'] == 'waiting_text':
            is_valid, error_msg = validate_text(text)
            if not is_valid:
                bot.reply_to(message, f"{EMOJIS['error']} {error_msg}")
                return
            
            cipher_data = db.get_cipher(state['cipher_id'])
            cipher = Cipher.from_dict(cipher_data)
            
            encrypted, errors = cipher.encrypt(text)
            db.add_to_history(user_id, state['cipher_id'], text, encrypted, 'encrypt')
            
            result_text = f"{EMOJIS['cipher']} *Зашифровано:*\n\n`{encrypted}`"
            
            if errors:
                result_text += f"\n\n⚠️ Не найдены: {', '.join(set(errors))}"
            
            bot.send_message(user_id, result_text, parse_mode='Markdown')
            del temp_data[f"encrypt_{user_id}"]
        
        return
    
    # ===== УМНАЯ РАСШИФРОВКА =====
    if f"decrypt_{user_id}" in temp_data:
        state = temp_data[f"decrypt_{user_id}"]
        
        if state['step'] == 'waiting_text':
            encrypted = text
            
            # Отправляем сообщение о начале анализа
            searching = bot.reply_to(
                message,
                f"{EMOJIS['magic']} *Анализирую текст...*\n"
                f"Проверяю все возможные методы шифрования...",
                parse_mode='Markdown'
            )
            
            # Получаем личные шифры пользователя
            ciphers = db.get_user_ciphers(user_id)
            
            # Запускаем умный анализ
            analyzer = SmartDecrypt(ciphers)
            results = analyzer.analyze(encrypted)
            
            # Удаляем сообщение о поиске
            bot.delete_message(user_id, searching.message_id)
            
            if not results:
                bot.send_message(
                    user_id,
                    UIMessages.no_results_found(),
                    parse_mode='Markdown'
                )
                del temp_data[f"decrypt_{user_id}"]
                return
            
            # Сохраняем результаты
            temp_data[f"decrypt_results_{user_id}"] = results
            
            # Показываем лучшие результаты
            bot.send_message(
                user_id,
                UIMessages.decrypt_results(results, show_all=False),
                parse_mode='Markdown',
                reply_markup=get_decrypt_results_keyboard(len(results))
            )
            
            del temp_data[f"decrypt_{user_id}"]
        
        return
    
    # ===== ЕСЛИ НИЧЕГО НЕ ПОДОШЛО =====
    else:
        bot.reply_to(
            message,
            f"{EMOJIS['info']} Используйте меню для работы с ботом!\n"
            f"Нажмите /start чтобы увидеть команды."
        )
