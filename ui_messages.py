# ui_messages.py - КРАСИВЫЕ СООБЩЕНИЯ ДЛЯ ИНТЕРФЕЙСА
from config import EMOJIS

class UIMessages:
    """Класс с красивыми сообщениями"""
    
    # Разделители
    SEPARATORS = {
        'line': '─' * 30,
        'double': '═' * 30,
        'dotted': '┄' * 30,
        'stars': '★' * 30,
        'hearts': '❤️' * 15,
        'zaps': '⚡' * 15,
        'crown': '👑' * 15,
    }
    
    @staticmethod
    def welcome_message(username: str) -> str:
        """Приветственное сообщение"""
        return f"""
✨ *ДОБРО ПОЖАЛОВАТЬ В CIPHERBOT* ✨
{UIMessages.SEPARATORS['stars']}

{EMOJIS['heart']} Привет, *{username}*!

Я твой личный помощник по шифрованию.
Умею работать с любыми символами и эмодзи!

{EMOJIS['crown']} *МОИ ВОЗМОЖНОСТИ:*
{EMOJIS['cipher']} • Свои шифры из эмодзи
🔢 • Шифр Цезаря
🪞 • Шифр Атбаш  
🔑 • Шифр Виженера
⚡ • Азбука Морзе
⌨️ • Смена раскладки

{EMOJIS['magic']} *УМНАЯ РАСШИФРОВКА:*
Просто отправь мне любое сообщение,
и я сам найду способ его расшифровать!

{UIMessages.SEPARATORS['hearts']}
Выбери действие в меню ниже {EMOJIS['heart']}
"""
    
    @staticmethod
    def smart_decrypt_intro() -> str:
        """Введение в умную расшифровку"""
        return f"""
{EMOJIS['magic']} *УМНАЯ РАСШИФРОВКА* {EMOJIS['magic']}
{UIMessages.SEPARATORS['dotted']}

{EMOJIS['search']} Отправь мне зашифрованное сообщение,
и я автоматически определю метод расшифровки:

{EMOJIS['cipher']} • Твои личные шифры
🔢 • Шифр Цезаря
🪞 • Шифр Атбаш
🔑 • Шифр Виженера
⚡ • Азбука Морзе
⌨️ • Раскладка клавиатуры

⚡ *Поддерживаются:*
• Все буквы (рус/англ)
• Все цифры (включая 6️⃣)
• Все знаки препинания
• Все эмодзи

{UIMessages.SEPARATORS['line']}
Жду твоё сообщение {EMOJIS['heart']}
"""
    
    @staticmethod
    def decrypt_results(results: list, show_all: bool = False) -> str:
        """Форматирует результаты расшифровки"""
        if not results:
            return f"{EMOJIS['error']} *Ничего не найдено*"
        
        if show_all:
            title = f"{EMOJIS['magic']} *ВСЕ РЕЗУЛЬТАТЫ* {EMOJIS['magic']}"
        else:
            title = f"{EMOJIS['magic']} *ЛУЧШИЕ РЕЗУЛЬТАТЫ* {EMOJIS['magic']}"
        
        output = f"""
{title}
{UIMessages.SEPARATORS['double']}

Найдено вариантов: *{len(results)}*

"""
        for i, res in enumerate(results[:5] if not show_all else results, 1):
            medal = '🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '📌'
            
            # Определяем иконку по типу
            icon = res.get('icon', '📌')
            
            # Обрезаем длинный результат
            short_res = res['result'][:100] + '...' if len(res['result']) > 100 else res['result']
            
            output += f"{medal} *{icon} {res['name']}*\n"
            output += f"   📊 *Точность:* {res['score']:.1f}%\n"
            output += f"   📝 `{short_res}`\n\n"
            
            if len(output) > 3000 and not show_all:
                output += f"{UIMessages.SEPARATORS['line']}\n... и ещё результаты"
                break
        
        output += UIMessages.SEPARATORS['line']
        return output
    
    @staticmethod
    def no_results_found() -> str:
        """Сообщение когда ничего не найдено"""
        return f"""
{EMOJIS['error']} *НЕ УДАЛОСЬ РАСШИФРОВАТЬ*
{UIMessages.SEPARATORS['dotted']}

Я проверил все возможные методы:
{EMOJIS['cipher']} Личные шифры
⚡ Азбука Морзе
⌨️ Раскладка клавиатуры
🔢 Цезарь (33 варианта)
🪞 Атбаш

*Возможные причины:*
• Текст слишком короткий
• Использован неизвестный метод
• Текст не зашифрован

{EMOJIS['help']} Попробуйте выбрать конкретный метод в меню
"""
    
    @staticmethod
    def cipher_created(name: str, preview: str) -> str:
        """Сообщение о создании шифра"""
        return f"""
{EMOJIS['success']} *ШИФР УСПЕШНО СОЗДАН* {EMOJIS['success']}
{UIMessages.SEPARATORS['stars']}

📛 *Название:* {name}

{preview}

{UIMessages.SEPARATORS['hearts']}
Теперь вы можете использовать его для шифрования!
"""
    
    @staticmethod
    def help_message() -> str:
        """Справка по использованию"""
        return f"""
{EMOJIS['help']} *КАК ПОЛЬЗОВАТЬСЯ БОТОМ* {EMOJIS['help']}
{UIMessages.SEPARATORS['double']}

*📝 ОСНОВНЫЕ КОМАНДЫ:*

{EMOJIS['cipher']} *Зашифровать*
   Использует ваш личный шифр для шифрования текста

{EMOJIS['decipher']} *Расшифровать*
   Умный режим - сам определяет метод расшифровки

{EMOJIS['key']} *Мои шифры*
   Управление вашими личными шифрами

*🔢 БАЗОВЫЕ ШИФРЫ:*

🔢 *Цезарь* - сдвиг букв на 3 позиции
🪞 *Атбаш* - зеркальный шифр (А=Я, Б=Ю)
🔑 *Виженер* - шифр с ключевым словом

*⚡ СПЕЦИАЛЬНЫЕ:*

⚡ *Морзе* - азбука Морзе
⌨️ *Раскладка* - смена RU/EN клавиатуры

{UIMessages.SEPARATORS['stars']}
*📤 ПОДЕЛИТЬСЯ:*
1. Зайдите в "Мои шифры"
2. Выберите шифр
3. Нажмите "Поделиться"
4. Выберите способ (ссылка, QR-код, код)

{EMOJIS['magic']} *УМНАЯ РАСШИФРОВКА:*
Просто отправьте любое зашифрованное сообщение!
"""
    
    @staticmethod
    def share_cipher(cipher_name: str, link: str = None, code: str = None) -> str:
        """Сообщение для шаринга шифра"""
        msg = f"""
{EMOJIS['share']} *ПОДЕЛИТЬСЯ ШИФРОМ* {EMOJIS['share']}
{UIMessages.SEPARATORS['stars']}

📛 *Шифр:* {cipher_name}

"""
        if link:
            msg += f"""
🔗 *ССЫЛКА-ПРИГЛАШЕНИЕ:*
Перешли это сообщение другу:
`{link}`
"""
        elif code:
            msg += f"""
🔑 *КОД ДЛЯ ИМПОРТА:*
Скопируй и отправь другу:
`{code}`
"""
        
        msg += f"""
{UIMessages.SEPARATORS['hearts']}
Друг перейдёт по ссылке или вставит код
и получит твой шифр!
"""
        return msg
    
    @staticmethod
    def stats_message(ciphers_count: int, history_count: int, last_date: str = None) -> str:
        """Статистика пользователя"""
        return f"""
{EMOJIS['stats']} *ТВОЯ СТАТИСТИКА* {EMOJIS['stats']}
{UIMessages.SEPARATORS['double']}

{EMOJIS['key']} *Шифров создано:* {ciphers_count}
{EMOJIS['cipher']} *Операций:* {history_count}

⏰ *Последняя активность:*
{last_date or 'нет данных'}

{UIMessages.SEPARATORS['line']}
Продолжай в том же духе! 🔥
"""
