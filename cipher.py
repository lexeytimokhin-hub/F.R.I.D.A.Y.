# cipher.py - ПОЛНАЯ ПОДДЕРЖКА ВСЕХ СИМВОЛОВ И ЭМОДЗИ
import random
import json
import base64
from typing import Dict, Tuple, List

class EmojiHelper:
    """Встроенный помощник для работы с эмодзи и спецсимволами"""
    
    # Словарь для нормализации составных эмодзи
    COMPOUND_EMOJIS = {
        '0⃣': '0️⃣', '1⃣': '1️⃣', '2⃣': '2️⃣', '3⃣': '3️⃣', '4⃣': '4️⃣',
        '5⃣': '5️⃣', '6⃣': '6️⃣', '7⃣': '7️⃣', '8⃣': '8️⃣', '9⃣': '9️⃣',
        '#⃣': '#️⃣', '*⃣': '*️⃣',
    }
    
    # Вариационные селекторы
    VARIATION_SELECTORS = ['\uFE0F', '\uFE0E', '\u20E3']
    
    @staticmethod
    def normalize_emoji(text: str) -> str:
        """Нормализует составные эмодзи"""
        for compound, standard in EmojiHelper.COMPOUND_EMOJIS.items():
            text = text.replace(compound, standard)
        return text
    
    @staticmethod
    def split_text_into_chars(text: str) -> list:
        """Правильно разбивает текст на символы с учетом эмодзи"""
        result = []
        i = 0
        while i < len(text):
            # Проверяем на составные эмодзи (до 3 символов)
            found = False
            for j in range(3, 0, -1):
                if i + j <= len(text):
                    chunk = text[i:i+j]
                    # Проверяем наличие вариационных селекторов
                    if any(sel in chunk for sel in EmojiHelper.VARIATION_SELECTORS):
                        result.append(chunk)
                        i += j
                        found = True
                        break
                    # Проверяем по словарю
                    if chunk in EmojiHelper.COMPOUND_EMOJIS:
                        result.append(chunk)
                        i += j
                        found = True
                        break
            
            if not found:
                result.append(text[i])
                i += 1
        
        return result
    
    @staticmethod
    def is_emoji(char: str) -> bool:
        """Проверяет, является ли символ эмодзи"""
        if len(char) > 1:
            return True
        code = ord(char)
        # Основные диапазоны эмодзи
        return (0x2000 <= code <= 0x2BFF or
                0xE000 <= code <= 0xF8FF or
                0x1F000 <= code <= 0x1FFFF or
                0x2700 <= code <= 0x27BF)


class Cipher:
    """Класс для работы с шифрами (поддерживает все символы)"""
    
    # ПОЛНЫЙ РУССКИЙ АЛФАВИТ
    RUSSIAN_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    
    # АНГЛИЙСКИЙ АЛФАВИТ
    ENGLISH_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    
    # ЦИФРЫ
    DIGITS = "0123456789"
    
    # ВСЕ ЗНАКИ ПРЕПИНАНИЯ
    PUNCTUATION = ".,!?:;\"'()[]{}<>-—…«»*&^%$#@+-=/\\|`~"
    
    # ПРОБЕЛЬНЫЕ СИМВОЛЫ
    WHITESPACE = " \n\t\r"
    
    # ПОЛНЫЙ АЛФАВИТ СО ВСЕМИ СИМВОЛАМИ
    FULL_ALPHABET = (RUSSIAN_ALPHABET + RUSSIAN_ALPHABET.upper() + 
                     ENGLISH_ALPHABET + ENGLISH_ALPHABET.upper() + 
                     DIGITS + PUNCTUATION + WHITESPACE)
    
    def __init__(self, name: str = "Мой шифр"):
        self.name = name
        self.cipher_map = {}
        self.reverse_map = {}
        self.created_at = None
        self.updated_at = None
    
    def generate_random(self, alphabet_type: str = "full"):
        """Генерирует случайный шифр с красивыми эмодзи"""
        if alphabet_type == "russian":
            alphabet = self.RUSSIAN_ALPHABET
        else:
            alphabet = self.FULL_ALPHABET
        
        # Красивые эмодзи для шифрования
        emoji_pool = [
            '🌟', '✨', '⭐', '🌙', '☀️', '🌈', '⚡', '🔥', '💧', '🌊',
            '🌍', '🌎', '🌏', '🍀', '🌺', '🌸', '🌼', '🍂', '🍁', '🌿',
            '🍃', '🌵', '🌴', '🌾', '🌻', '🌷', '🌹', '🥀', '🍄', '🌰',
            '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯',
            '🦁', '🐮', '🐷', '🐸', '🐙', '🦑', '🦐', '🦞', '🐟', '🐠',
            '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣',
            '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔',
            '🎉', '🎊', '🎈', '🎁', '🎀', '🎄', '🎃', '🎆', '🎇', '🧨',
        ]
        
        # Убеждаемся, что хватит эмодзи
        while len(emoji_pool) < len(alphabet):
            emoji_pool.extend(emoji_pool)
        
        random.shuffle(emoji_pool)
        selected = emoji_pool[:len(alphabet)]
        
        self.cipher_map = dict(zip(alphabet, selected))
        self.reverse_map = {v: k for k, v in self.cipher_map.items()}
        return self.cipher_map
    
    def encrypt(self, text: str) -> Tuple[str, List[str]]:
        """Шифрует текст с полной поддержкой всех символов"""
        result = []
        errors = []
        
        # Разбиваем на символы с учетом эмодзи
        chars = EmojiHelper.split_text_into_chars(text)
        
        for char in chars:
            normalized = EmojiHelper.normalize_emoji(char)
            
            if normalized in self.cipher_map:
                result.append(self.cipher_map[normalized])
            elif char in self.cipher_map:
                result.append(self.cipher_map[char])
            else:
                # Если символ не найден в шифре
                result.append(char)
                if char.strip() and not EmojiHelper.is_emoji(char):
                    errors.append(char)
        
        return ''.join(result), list(set(errors))
    
    def decrypt(self, text: str) -> Tuple[str, List[str]]:
        """Расшифровывает текст с полной поддержкой всех символов"""
        result = []
        errors = []
        
        # Разбиваем на символы с учетом эмодзи
        chars = EmojiHelper.split_text_into_chars(text)
        i = 0
        
        while i < len(chars):
            found = False
            current = chars[i]
            normalized = EmojiHelper.normalize_emoji(current)
            
            # Проверяем текущий символ
            if current in self.reverse_map:
                result.append(self.reverse_map[current])
                i += 1
                continue
            
            if normalized in self.reverse_map:
                result.append(self.reverse_map[normalized])
                i += 1
                continue
            
            # Проверяем составные символы (до 3 подряд)
            for j in range(min(3, len(chars) - i), 0, -1):
                combined = ''.join(chars[i:i+j])
                norm_combined = EmojiHelper.normalize_emoji(combined)
                
                if combined in self.reverse_map:
                    result.append(self.reverse_map[combined])
                    i += j
                    found = True
                    break
                
                if norm_combined in self.reverse_map:
                    result.append(self.reverse_map[norm_combined])
                    i += j
                    found = True
                    break
            
            if not found:
                # Не нашли в шифре
                result.append(current)
                if current.strip() and not EmojiHelper.is_emoji(current):
                    errors.append(current)
                i += 1
        
        return ''.join(result), list(set(errors))
    
    def get_preview(self, count: int = 10) -> str:
        """Красивое превью шифра"""
        preview = f"🔐 *{self.name}*\n"
        preview += "╭" + "─" * 30 + "╮\n"
        
        # Показываем русские буквы
        russian_items = []
        for letter in self.RUSSIAN_ALPHABET:
            if letter in self.cipher_map:
                russian_items.append((letter, self.cipher_map[letter]))
        
        for i, (letter, emoji) in enumerate(russian_items[:count]):
            preview += f"│ `{letter}` → {emoji} "
            if i % 2 == 1:
                preview += "│\n"
        
        if len(russian_items) > count:
            preview += f"│ ... и еще {len(russian_items) - count} букв │\n"
        
        preview += "╰" + "─" * 30 + "╯"
        return preview
    
    def export_to_string(self) -> str:
        """Экспорт в строку"""
        try:
            data = {
                'name': self.name,
                'cipher_map': self.cipher_map,
                'version': '2.0'
            }
            json_str = json.dumps(data, ensure_ascii=False)
            encoded = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
            return f"CIPHERv2:{encoded}"
        except:
            return "ОШИБКА_ЭКСПОРТА"
    
    @classmethod
    def import_from_string(cls, text: str):
        """Импорт из строки"""
        try:
            text = text.strip()
            if text.startswith('CIPHERv2:'):
                encoded = text.replace('CIPHERv2:', '')
            elif text.startswith('CIPHER:'):
                encoded = text.replace('CIPHER:', '')
            else:
                return None
            
            json_str = base64.b64decode(encoded.encode('utf-8')).decode('utf-8')
            data = json.loads(json_str)
            
            cipher = cls(data.get('name', 'Импорт'))
            cipher.cipher_map = data.get('cipher_map', {})
            cipher.reverse_map = {v: k for k, v in cipher.cipher_map.items()}
            return cipher
        except:
            return None
    
    def rename(self, new_name: str) -> bool:
        """Переименование шифра"""
        if new_name and new_name.strip():
            self.name = new_name.strip()
            return True
        return False
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'cipher_map': self.cipher_map,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cipher':
        cipher = cls(data.get('name', 'Без названия'))
        cipher.cipher_map = data.get('cipher_map', {})
        cipher.reverse_map = {v: k for k, v in cipher.cipher_map.items()}
        cipher.created_at = data.get('created_at')
        cipher.updated_at = data.get('updated_at')
        return cipher
