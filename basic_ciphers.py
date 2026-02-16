# basic_ciphers.py - Базовые шифры (полная версия)
import random
import string
from typing import Dict, Tuple, List

class BasicCiphers:
    """Класс с базовыми шифрами"""
    
    # ============================================
    # ШИФР ЦЕЗАРЯ
    # ============================================
    @staticmethod
    def caesar_encrypt(text: str, shift: int = 3) -> str:
        """Шифр Цезаря (сдвиг)"""
        result = []
        for char in text.lower():
            if 'а' <= char <= 'я' or char == 'ё':
                # Русские буквы
                if char == 'ё':
                    char = 'е'
                code = ord(char) - ord('а')
                new_code = (code + shift) % 32
                new_char = chr(ord('а') + new_code)
                result.append(new_char)
            elif 'a' <= char <= 'z':
                # Английские буквы
                code = ord(char) - ord('a')
                new_code = (code + shift) % 26
                result.append(chr(ord('a') + new_code))
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def caesar_decrypt(text: str, shift: int = 3) -> str:
        """Расшифровка Цезаря"""
        return BasicCiphers.caesar_encrypt(text, -shift)
    
    # ============================================
    # ШИФР АТБАШ (ЗЕРКАЛЬНЫЙ)
    # ============================================
    @staticmethod
    def atbash_encrypt(text: str) -> str:
        """Атбаш - А=Я, Б=Ю, и т.д."""
        result = []
        for char in text.lower():
            if 'а' <= char <= 'я' or char == 'ё':
                if char == 'ё':
                    char = 'е'
                # А=Я, Б=Ю, В=Э...
                pos = ord(char) - ord('а')
                mirror_pos = 31 - pos
                result.append(chr(ord('а') + mirror_pos))
            elif 'a' <= char <= 'z':
                # A=Z, B=Y...
                pos = ord(char) - ord('a')
                result.append(chr(ord('z') - pos))
            else:
                result.append(char)
        return ''.join(result)
    
    atbash_decrypt = atbash_encrypt  # Атбаш симметричен
    
    # ============================================
    # ШИФР ВИЖЕНЕРА
    # ============================================
    @staticmethod
    def vigenere_encrypt(text: str, key: str) -> str:
        """Шифр Виженера"""
        if not key:
            return text
        
        result = []
        key = key.lower()
        key_len = len(key)
        key_pos = 0
        
        for char in text.lower():
            if 'а' <= char <= 'я' or char == 'ё':
                if char == 'ё':
                    char = 'е'
                # Берем букву ключа
                key_char = key[key_pos % key_len]
                if 'а' <= key_char <= 'я':
                    if key_char == 'ё':
                        key_char = 'е'
                    key_shift = ord(key_char) - ord('а')
                else:
                    key_shift = 0
                
                # Шифруем
                pos = ord(char) - ord('а')
                new_pos = (pos + key_shift) % 32
                result.append(chr(ord('а') + new_pos))
                key_pos += 1
            else:
                result.append(char)
        
        return ''.join(result)
    
    @staticmethod
    def vigenere_decrypt(text: str, key: str) -> str:
        """Расшифровка Виженера"""
        if not key:
            return text
        
        result = []
        key = key.lower()
        key_len = len(key)
        key_pos = 0
        
        for char in text.lower():
            if 'а' <= char <= 'я':
                key_char = key[key_pos % key_len]
                if 'а' <= key_char <= 'я':
                    if key_char == 'ё':
                        key_char = 'е'
                    key_shift = ord(key_char) - ord('а')
                else:
                    key_shift = 0
                
                pos = ord(char) - ord('а')
                new_pos = (pos - key_shift) % 32
                result.append(chr(ord('а') + new_pos))
                key_pos += 1
            else:
                result.append(char)
        
        return ''.join(result)


# ============================================
# ШИФР РАСКЛАДКИ КЛАВИАТУРЫ
# ============================================
class KeyboardCipher:
    """Шифр на основе раскладки клавиатуры"""
    
    # Соответствие русской и английской раскладки
    RU_TO_EN = {
        'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y',
        'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']',
        'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h',
        'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';', 'э': "'",
        'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n',
        'ь': 'm', 'б': ',', 'ю': '.', 'ё': '`'
    }
    
    EN_TO_RU = {v: k for k, v in RU_TO_EN.items()}
    
    # Заглавные буквы
    RU_TO_EN_UPPER = {
        'Й': 'Q', 'Ц': 'W', 'У': 'E', 'К': 'R', 'Е': 'T', 'Н': 'Y',
        'Г': 'U', 'Ш': 'I', 'Щ': 'O', 'З': 'P', 'Х': '{', 'Ъ': '}',
        'Ф': 'A', 'Ы': 'S', 'В': 'D', 'А': 'F', 'П': 'G', 'Р': 'H',
        'О': 'J', 'Л': 'K', 'Д': 'L', 'Ж': ':', 'Э': '"',
        'Я': 'Z', 'Ч': 'X', 'С': 'C', 'М': 'V', 'И': 'B', 'Т': 'N',
        'Ь': 'M', 'Б': '<', 'Ю': '>', 'Ё': '~'
    }
    
    EN_TO_RU_UPPER = {v: k for k, v in RU_TO_EN_UPPER.items()}
    
    @classmethod
    def ru_to_en(cls, text: str) -> str:
        """Конвертирует русский текст в английскую раскладку"""
        result = []
        for char in text:
            if char in cls.RU_TO_EN:
                result.append(cls.RU_TO_EN[char])
            elif char in cls.RU_TO_EN_UPPER:
                result.append(cls.RU_TO_EN_UPPER[char])
            else:
                result.append(char)
        return ''.join(result)
    
    @classmethod
    def en_to_ru(cls, text: str) -> str:
        """Конвертирует английский текст в русскую раскладку"""
        result = []
        for char in text:
            if char in cls.EN_TO_RU:
                result.append(cls.EN_TO_RU[char])
            elif char in cls.EN_TO_RU_UPPER:
                result.append(cls.EN_TO_RU_UPPER[char])
            else:
                result.append(char)
        return ''.join(result)
    
    @classmethod
    def encrypt(cls, text: str) -> str:
        """Шифрование сменой раскладки (RU→EN)"""
        return cls.ru_to_en(text)
    
    @classmethod
    def decrypt(cls, text: str) -> str:
        """Расшифровка сменой раскладки (EN→RU)"""
        return cls.en_to_ru(text)


# ============================================
# УЛУЧШЕННОЕ РАСПОЗНАВАНИЕ ЭМОДЗИ
# ============================================
class EmojiHelper:
    """Помощник для работы с эмодзи"""
    
    @staticmethod
    def split_emoji_text(text: str) -> List[str]:
        """Разбивает текст на символы с учетом эмодзи"""
        result = []
        i = 0
        while i < len(text):
            # Проверяем возможные эмодзи (они могут быть длиной 2)
            found = False
            for length in [2, 1]:
                if i + length <= len(text):
                    chunk = text[i:i+length]
                    # Проверяем, похоже ли на эмодзи (обычно юникод > 0x2000)
                    if length == 2 and ord(chunk[0]) > 0x2000:
                        result.append(chunk)
                        i += length
                        found = True
                        break
                    elif length == 1:
                        if ord(chunk) > 0x2000:
                            result.append(chunk)
                            i += length
                            found = True
                            break
            if not found:
                result.append(text[i])
                i += 1
        return result
    
    @staticmethod
    def clean_emoji_text(text: str) -> str:
        """Очищает текст от эмодзи (оставляет только буквы и цифры)"""
        result = []
        for char in text:
            if ord(char) < 0x2000:  # Не эмодзи
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def extract_emojis(text: str) -> List[str]:
        """Извлекает все эмодзи из текста"""
        emojis = []
        i = 0
        while i < len(text):
            for length in [2, 1]:
                if i + length <= len(text):
                    chunk = text[i:i+length]
                    if length == 2 and ord(chunk[0]) > 0x2000:
                        emojis.append(chunk)
                        i += length
                        break
                    elif length == 1 and ord(chunk) > 0x2000:
                        emojis.append(chunk)
                        i += length
                        break
            else:
                i += 1
        return emojis
