# handlers.py - ПОЛНАЯ ВЕРСИЯ С ПЕРЕИМЕНОВАНИЕМ
import telebot
from telebot import types
import time

from config import TOKEN, EMOJIS
from cipher import Cipher
from database import Database
from keyboards import *
from utils import *

# Добавляем недостающие эмодзи
if 'search' not in EMOJIS:
    EMOJIS['search'] = '🔍'
if 'decipher' not in EMOJIS:
    EMOJIS['decipher'] = '🔓'
if 'cipher' not in EMOJIS:
    EMOJIS['cipher'] = '🔐'

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
    
    welcome_text = f"""
{EMOJIS['heart']} *Добро пожаловать в CipherBot!*

✨ *ФУНКЦИИ:*
• 🔐 Зашифровать сообщение
• 🔓 Авторасшифровка (сам найдет шифр)
• 🔑 Мои шифры
• 📤 Поделиться шифром
• ✏️ Переименовать шифр

*Как начать:*
1. Создайте шифр в разделе "Мои шифры"
2. Для расшифровки просто отправьте сообщение
    """
    
    bot.send_message(
        user.id, 
        welcome_text, 
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
        f"{EMOJIS['decipher']} *Авторасшифровка*\n\n"
        f"{EMOJIS['search']} Отправьте зашифрованное сообщение.\n"
        f"Я сам найду нужный шифр!",
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
            f"{EMOJIS['star']} *Создан ваш первый шифр!*\n\n"
            f"{cipher.get_preview()}",
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
    
    stats_text = f"""
{EMOJIS['info']} *Ваша статистика:*

• Всего шифров: {len(ciphers)}
• Последняя операция: {format_time(history[0]['created_at']) if history else 'нет'}
    """
    
    bot.send_message(
        user_id,
        stats_text,
        parse_mode='Markdown',
        reply_markup=get_settings_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == f"{EMOJIS['help']} Помощь")
def show_help(message):
    help_text = f"""
{EMOJIS['help']} *Как пользоваться ботом*

*📝 Команды:*
• Зашифровать - превратить текст в шифр
• Расшифровать - восстановить текст (автоподбор)
• Мои шифры - управление шифрами
• ✏️ Переименовать - изменить название шифра

*📤 Поделиться:*
1. Зайдите в "Мои шифры"
2. Выберите шифр → "Поделиться"

*🔍 Авторасшифровка:*
Бот сам найдет нужный шифр среди всех ваших!
    """
    
    bot.send_message(
        message.from_user.id,
        help_text,
        parse_mode='Markdown',
        reply_markup=get_back_keyboard()
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
            f"{EMOJIS['success']} *Шифр создан!*\n\n"
            f"{cipher.get_preview()}",
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
        
        link_text = f"""
{EMOJIS['link']} *Ссылка-приглашение:*

Перешлите это сообщение другу:

`{invite_link}`

Когда друг перейдет по ссылке, он сможет добавить ваш шифр себе!
        """
        
        bot.edit_message_text(
            link_text,
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
                caption=f"{EMOJIS['qr']} *QR-код для шифра*\n\n"
                        f"🔑 *{cipher.name}*\n\n"
                        f"Друг может отсканировать этот код и получить шифр!",
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
            
            code_text = f"""
{EMOJIS['key']} *КОД ДЛЯ ИМПОРТА*

Скопируйте этот код и отправьте другу:

`{import_code}`

*Как использовать:*
1. Друг нажимает "Импорт" в меню
2. Вставляет этот код
3. Получает ваш шифр
            """
            
            bot.edit_message_text(
                code_text,
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
                f"{EMOJIS['success']} *Шифр успешно добавлен!*\n\n"
                f"{cipher.get_preview()}",
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
    
    # ===== ПЕРЕИМЕНОВАНИЕ ШИФРА (НОВОЕ!) =====
    if data.startswith("rename_cipher_"):
        cipher_id = int(data.split("_")[2])
        
        # Сохраняем в временные данные
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
        first_le
