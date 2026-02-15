# handlers.py - ФИНАЛЬНАЯ ВЕРСИЯ
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
# ОБРАБОТКА ВСЕХ СООБЩЕНИЙ (СТИКЕРЫ ТОЖЕ)
# ============================================
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    
    # Если это не текст - просто игнорируем (но не удаляем)
    if message.content_type != 'text':
        return
    
    text = message.text
    
    # Игнорируем команды и кнопки
    if text.startswith('/') or text in [f"{EMOJIS['cipher']} Зашифровать", 
                                         f"{EMOJIS['decipher']} Расшифровать",
                                         f"{EMOJIS['key']} Мои шифры",
                                         f"{EMOJIS['share']} Поделиться",
                                         f"{EMOJIS['settings']} Настройки",
                                         f"{EMOJIS['help']} Помощь"]:
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
                    f"{EMOJIS['success']} *Шифр успешно импортирован!*\n\n"
                    f"{cipher.get_preview()}",
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
                f"{EMOJIS['error']} Ошибка при импорте. Проверьте код."
            )
        return
    
    # ===== СМЕНА ШИФРА =====
    if f"changing_{user_id}" in temp_data:
        change_data = temp_data[f"changing_{user_id}"]
        current_index = change_data['current_letter_index']
        cipher = change_data['cipher']
        new_map = change_data['new_map']
        
        russian_letters = list("абвгдеёжзийклмнопрстуфхцчшщъыьэюя")
        
        if not text:
            bot.reply_to(message, "Пожалуйста, отправьте символ для этой буквы!")
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
    
    # ===== АВТОРАСШИФРОВКА =====
    if f"decrypt_{user_id}" in temp_data:
        state = temp_data[f"decrypt_{user_id}"]
        
        if state['step'] == 'waiting_text':
            encrypted = text
            ciphers = db.get_user_ciphers(user_id)
            
            if not ciphers:
                bot.reply_to(message, f"{EMOJIS['error']} У вас нет шифров!")
                del temp_data[f"decrypt_{user_id}"]
                return
            
            # Поиск
            searching = bot.reply_to(message, f"{EMOJIS['search']} 🔍 Поиск...")
            
            results = []
            for cipher_info in ciphers:
                cipher = Cipher.from_dict(cipher_info['data'])
                decrypted, errors = cipher.decrypt(encrypted)
                
                total_chars = len(encrypted)
                error_chars = len(errors)
                score = (total_chars - error_chars) / total_chars * 100 if total_chars > 0 else 0
                
                results.append({
                    'cipher': cipher,
                    'decrypted': decrypted,
                    'cipher_id': cipher_info['id'],
                    'cipher_name': cipher_info['name'],
                    'score': score,
                    'errors': errors
                })
            
            bot.delete_message(user_id, searching.message_id)
            
            if not results:
                bot.reply_to(message, f"{EMOJIS['error']} Не удалось расшифровать!")
                del temp_data[f"decrypt_{user_id}"]
                return
            
            # Сортируем
            results.sort(key=lambda x: x['score'], reverse=True)
            best = results[0]
            
            # Если точность太低
            if best['score'] < 30:
                response = f"{EMOJIS['warning']} *Низкая точность*\n\n"
                response += f"Шифр: *{best['cipher_name']}*\n"
                response += f"Точность: {best['score']:.1f}%\n\n"
                response += f"Результат:\n`{best['decrypted']}`"
                
                bot.reply_to(message, response, parse_mode='Markdown')
                del temp_data[f"decrypt_{user_id}"]
                return
            
            # Показываем топ-3
            response = f"{EMOJIS['decipher']} *Результаты*\n\n"
            
            for i, res in enumerate(results[:3], 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                response += f"{medal} *{res['cipher_name']}* - {res['score']:.1f}%\n"
                response += f"`{res['decrypted'][:50]}`\n\n"
            
            keyboard = types.InlineKeyboardMarkup(row_width=3)
            buttons = []
            for i, res in enumerate(results[:3], 1):
                buttons.append(types.InlineKeyboardButton(f"{i}", callback_data=f"decrypt_choose_{res['cipher_id']}"))
            keyboard.add(*buttons)
            keyboard.add(types.InlineKeyboardButton("❌ Отмена", callback_data="decrypt_cancel"))
            
            temp_data[f"decrypt_results_{user_id}"] = {
                'results': results[:3],
                'encrypted': encrypted
            }
            
            bot.send_message(user_id, response, parse_mode='Markdown', reply_markup=keyboard)
        
        return
    
    # ===== ЕСЛИ НИЧЕГО =====
    else:
        bot.reply_to(message, f"{EMOJIS['info']} Используйте меню или /start")

# ============================================
# ОБРАБОТКА КНОПОК
# ============================================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data
    
    # Навигация
    if data == "back_to_main":
        bot.edit_message_text("Главное меню", user_id, call.message.message_id, reply_markup=None)
        bot.send_message(user_id, "Выберите действие:", reply_markup=get_main_keyboard())
        return
    
    if data == "back_to_ciphers":
        ciphers = db.get_user_ciphers(user_id)
        bot.edit_message_text(f"{EMOJIS['key']} *Ваши шифры:*", user_id, call.message.message_id, 
                            parse_mode='Markdown', reply_markup=get_ciphers_keyboard(ciphers))
        return
    
    # Пагинация
    if data.startswith("ciphers_page_"):
        page = int(data.split("_")[2])
        ciphers = db.get_user_ciphers(user_id)
        bot.edit_message_reply_markup(user_id, call.message.message_id, 
                                    reply_markup=get_ciphers_keyboard(ciphers, page))
        return
    
    # Создание шифра
    if data == "new_cipher":
        bot.edit_message_text(f"{EMOJIS['save']} *Создание шифра*", user_id, call.message.message_id,
                            parse_mode='Markdown', reply_markup=get_new_cipher_keyboard())
        return
    
    if data == "random_cipher":
        cipher = Cipher(generate_cipher_name("Случайный шифр"))
        cipher.generate_random("russian")
        cipher_id = db.save_cipher(user_id, cipher)
        bot.edit_message_text(f"{EMOJIS['success']} *Шифр создан!*", user_id, call.message.message_id,
                            parse_mode='Markdown', reply_markup=get_cipher_actions_keyboard(cipher_id))
        return
    
    # Выбор шифра
    if data.startswith("select_cipher_"):
        cipher_id = int(data.split("_")[2])
        cipher_data = db.get_cipher(cipher_id)
        cipher = Cipher.from_dict(cipher_data)
        
        ciphers = db.get_user_ciphers(user_id)
        is_default = any(c['id'] == cipher_id and c['is_default'] for c in ciphers)
        
        bot.edit_message_text(f"{EMOJIS['key']} *{cipher.name}*", user_id, call.message.message_id,
                            parse_mode='Markdown', reply_markup=get_cipher_actions_keyboard(cipher_id, is_default))
        return
    
    # Использование шифра
    if data.startswith("use_cipher_"):
        cipher_id = int(data.split("_")[2])
        temp_data[f"encrypt_{user_id}"] = {'cipher_id': cipher_id, 'step': 'waiting_text'}
        bot.edit_message_text(f"{EMOJIS['cipher']} Отправьте текст:", user_id, call.message.message_id)
        return
    
    # Поделиться
    if data.startswith("share_cipher_"):
        cipher_id = int(data.split("_")[2])
        bot.edit_message_text("Выберите способ:", user_id, call.message.message_id,
                            reply_markup=get_share_options_keyboard(cipher_id))
        return
    
    # Текстовая ссылка
    if data.startswith("share_text_"):
        cipher_id = int(data.split("_")[2])
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start=shared_cipher_{cipher_id}"
        bot.edit_message_text(f"🔗 *Ссылка:*\n`{link}`", user_id, call.message.message_id, parse_mode='Markdown')
        return
    
    # Импорт
    if data == "import_cipher":
        temp_data[f"import_waiting_{user_id}"] = True
        bot.edit_message_text(f"{EMOJIS['import']} Отправьте код:", user_id, call.message.message_id)
        return
    
    if data.startswith("import_cipher_"):
        cipher_id = int(data.split("_")[2])
        if f"import_{user_id}" in temp_data:
            cipher_data = temp_data[f"import_{user_id}"]['cipher_data']
            cipher = Cipher.from_dict(cipher_data)
            cipher.name = f"{cipher.name} (копия)"
            db.save_cipher(user_id, cipher)
            bot.edit_message_text(f"{EMOJIS['success']} Шифр добавлен!", user_id, call.message.message_id)
            del temp_data[f"import_{user_id}"]
        return
    
    # Смена шифра
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
        
        bot.edit_message_text(f"✏️ *Буква 1/33:* **а**\nОтправьте символ:", 
                            user_id, call.message.message_id, parse_mode='Markdown')
        return
    
    # Установка основного
    if data.startswith("set_default_"):
        cipher_id = int(data.split("_")[2])
        if db.set_default_cipher(user_id, cipher_id):
            bot.answer_callback_query(call.id, "✅ Основной шифр установлен!")
        return
    
    # Удаление
    if data.startswith("delete_cipher_"):
        cipher_id = int(data.split("_")[2])
        bot.edit_message_text("⚠️ *Удалить?*", user_id, call.message.message_id,
                            parse_mode='Markdown', reply_markup=get_confirm_keyboard("delete", cipher_id))
        return
    
    if data.startswith("confirm_delete_"):
        cipher_id = int(data.split("_")[2])
        if db.delete_cipher(user_id, cipher_id):
            bot.answer_callback_query(call.id, "✅ Удалено!")
            ciphers = db.get_user_ciphers(user_id)
            bot.edit_message_text(f"{EMOJIS['key']} *Ваши шифры:*", user_id, call.message.message_id,
                                parse_mode='Markdown', reply_markup=get_ciphers_keyboard(ciphers))
        return
    
    # ===== АВТОРАСШИФРОВКА - ВЫБОР ВАРИАНТА =====
    if data.startswith("decrypt_choose_"):
        cipher_id = int(data.split("_")[2])
        
        if f"decrypt_results_{user_id}" in temp_data:
            results = temp_data[f"decrypt_results_{user_id}"]['results']
            encrypted = temp_data[f"decrypt_results_{user_id}"]['encrypted']
            
            selected = next((r for r in results if r['cipher_id'] == cipher_id), None)
            
            if selected:
                db.add_to_history(user_id, selected['cipher_id'], selected['decrypted'], encrypted, 'decrypt')
                
                result_text = f"{EMOJIS['decipher']} *Расшифровано:*\n\n"
                result_text += f"🔑 *{selected['cipher_name']}*\n"
                result_text += f"📊 Точность: {selected['score']:.1f}%\n\n"
                result_text += f"`{selected['decrypted']}`"
                
                bot.edit_message_text(result_text, user_id, call.message.message_id, parse_mode='Markdown')
                
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(f"{EMOJIS['decipher']} Ещё", callback_data="decrypt_again"))
                keyboard.add(types.InlineKeyboardButton(f"{EMOJIS['back']} Меню", callback_data="back_to_main"))
                bot.send_message(user_id, "Что дальше?", reply_markup=keyboard)
                
                del temp_data[f"decrypt_results_{user_id}"]
                if f"decrypt_{user_id}" in temp_data:
                    del temp_data[f"decrypt_{user_id}"]
        
        return
    
    # Отмена расшифровки
    if data == "decrypt_cancel":
        if f"decrypt_results_{user_id}" in temp_data:
            del temp_data[f"decrypt_results_{user_id}"]
        if f"decrypt_{user_id}" in temp_data:
            del temp_data[f"decrypt_{user_id}"]
        bot.edit_message_text("❌ Отменено", user_id, call.message.message_id, reply_markup=None)
        return
    
    # Повторная расшифровка
    if data == "decrypt_again":
        bot.delete_message(user_id, call.message.message_id)
        fake_msg = type('obj', (object,), {
            'from_user': type('obj', (object,), {'id': user_id}),
            'chat': type('obj', (object,), {'id': user_id}),
            'text': f"{EMOJIS['decipher']} Расшифровать"
        })
        decrypt_text(fake_msg)
        return
    
    # Отмена
    if data == "cancel":
        bot.edit_message_text("❌ Отменено", user_id, call.message.message_id, reply_markup=None)
        return
    
    # Статистика
    if data == "show_stats":
        ciphers = db.get_user_ciphers(user_id)
        history = db.get_history(user_id, limit=1000)
        bot.edit_message_text(f"📊 *Статистика*\n\nШифров: {len(ciphers)}\nОпераций: {len(history)}",
                            user_id, call.message.message_id, parse_mode='Markdown', reply_markup=get_back_keyboard())
        return
