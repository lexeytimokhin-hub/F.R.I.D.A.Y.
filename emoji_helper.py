# emoji_helper.py - ПОЛНОЕ РАСПОЗНАВАНИЕ ВСЕХ ЭМОДЗИ
import unicodedata

class EmojiHelper:
    """Помощник для работы с эмодзи и спецсимволами"""
    
    # Словарь для нормализации составных эмодзи
    COMPOUND_EMOJIS = {
        # Цифры с селекторами
        '0⃣': '0️⃣', '1⃣': '1️⃣', '2⃣': '2️⃣', '3⃣': '3️⃣', '4⃣': '4️⃣',
        '5⃣': '5️⃣', '6⃣': '6️⃣', '7⃣': '7️⃣', '8⃣': '8️⃣', '9⃣': '9️⃣',
        '🔟': '🔟',
        
        # Другие составные
        '#⃣': '#️⃣', '*⃣': '*️⃣',
        '❤️': '❤️', '✨': '✨', '⭐': '⭐', '🌟': '🌟', '💫': '💫',
        '⚡': '⚡', '☀️': '☀️', '🌙': '🌙', '🌈': '🌈', '🌊': '🌊',
    }
    
    # Все возможные вариационные селекторы
    VARIATION_SELECTORS = ['\uFE0F', '\uFE0E', '\u20E3', '\uFE0F\u20E3']
    
    @staticmethod
    def normalize_emoji(text: str) -> str:
        """Нормализует составные эмодзи в стандартную форму"""
        # Сначала пробуем нормализовать через Unicode
        normalized = unicodedata.normalize('NFKC', text)
        
        # Проверяем наши составные эмодзи
        for compound, standard in EmojiHelper.COMPOUND_EMOJIS.items():
            normalized = normalized.replace(compound, standard)
        
        return normalized
    
    @staticmethod
    def split_text_into_chars(text: str) -> list:
        """Правильно разбивает текст на символы с учетом составных эмодзи"""
        result = []
        i = 0
        length = len(text)
        
        while i < length:
            char = text[i]
            
            # Проверяем на составные эмодзи (до 4 символов)
            found = False
            for j in range(4, 0, -1):
                if i + j <= length:
                    chunk = text[i:i+j]
                    # Проверяем, похоже ли на эмодзи
                    if EmojiHelper.is_compound_emoji(chunk):
                        result.append(chunk)
                        i += j
                        found = True
                        break
            
            if not found:
                # Проверяем, является ли символ эмодзи
                if EmojiHelper.is_emoji(char):
                    result.append(char)
                    i += 1
                else:
                    result.append(char)
                    i += 1
        
        return result
    
    @staticmethod
    def is_compound_emoji(text: str) -> bool:
        """Проверяет, является ли текст составным эмодзи"""
        if len(text) < 2:
            return False
        
        # Проверяем наличие вариационных селекторов
        for selector in EmojiHelper.VARIATION_SELECTORS:
            if selector in text:
                return True
        
        # Проверяем по нашему словарю
        normalized = unicodedata.normalize('NFKC', text)
        return normalized in EmojiHelper.COMPOUND_EMOJIS
    
    @staticmethod
    def is_emoji(char: str) -> bool:
        """Проверяет, является ли символ эмодзи"""
        if len(char) > 1:
            return EmojiHelper.is_compound_emoji(char)
        
        code = ord(char)
        
        # Основные диапазоны эмодзи
        emoji_ranges = [
            (0x2000, 0x2BFF),   # Разные символы
            (0xE000, 0xF8FF),    # Private use area
            (0x1F000, 0x1FFFF),  # Дополнительные символы
            (0x2700, 0x27BF),    # Символы Dingbats
            (0x2600, 0x26FF),    # Разные символы
        ]
        
        for start, end in emoji_ranges:
            if start <= code <= end:
                return True
        
        # Конкретные эмодзи
        common_emojis = '❤️🔥✨⭐🌟💫⚡☀️🌙🌈🌊🎉🎊🎈🎁🎀🎄🎃🎆🎇🧨'
        return char in common_emojis
    
    @staticmethod
    def extract_emojis(text: str) -> list:
        """Извлекает все эмодзи из текста"""
        chars = EmojiHelper.split_text_into_chars(text)
        return [c for c in chars if EmojiHelper.is_emoji(c)]
    
    @staticmethod
    def clean_text_from_emojis(text: str) -> str:
        """Удаляет эмодзи из текста"""
        chars = EmojiHelper.split_text_into_chars(text)
        clean = [c for c in chars if not EmojiHelper.is_emoji(c)]
        return ''.join(clean)
    
    @staticmethod
    def count_emojis(text: str) -> int:
        """Считает количество эмодзи"""
        return len(EmojiHelper.extract_emojis(text))
    
    @staticmethod
    def emoji_to_description(emoji: str) -> str:
        """Преобразует эмодзи в описание"""
        descriptions = {
            '6️⃣': 'цифра_шесть',
            '5️⃣': 'цифра_пять',
            '4️⃣': 'цифра_четыре',
            '3️⃣': 'цифра_три',
            '2️⃣': 'цифра_два',
            '1️⃣': 'цифра_один',
            '0️⃣': 'цифра_ноль',
            '🔟': 'десять',
            '#️⃣': 'решетка',
            '*️⃣': 'звездочка',
            '❤️': 'сердце',
            '🔥': 'огонь',
            '✨': 'искры',
            '⭐': 'звезда',
            '🌟': 'сияющая_звезда',
            '💫': 'звездочки',
            '⚡': 'молния',
            '☀️': 'солнце',
            '🌙': 'луна',
            '🌈': 'радуга',
            '🌊': 'волна',
            '🎉': 'хлопушка',
            '🎊': 'конфетти',
            '🎈': 'шарик',
            '🎁': 'подарок',
            '🎀': 'бант',
            '🎄': 'елка',
            '🎃': 'тыква',
            '🎆': 'фейерверк',
            '🎇': 'бенгальский_огонь',
            '🧨': 'петарда',
        }
        return descriptions.get(emoji, f'эмодзи_{ord(emoji[0])}')
