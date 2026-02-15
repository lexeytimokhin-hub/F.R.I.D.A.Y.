# cipher.py - ПОЛНАЯ ВЕРСИЯ С ЭКСПОРТОМ/ИМПОРТОМ
import random
import json
import base64
from typing import Dict, Tuple, List

class Cipher:
    """Класс для работы с шифрами"""
    
    # ============================================
    # ПОЛНЫЙ РУССКИЙ АЛФАВИТ (33 БУКВЫ)
    # ============================================
    RUSSIAN_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    
    # АНГЛИЙСКИЕ БУКВЫ (ДОПОЛНИТЕЛЬНО)
    ENGLISH_ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    
    # ЦИФРЫ И СИМВОЛЫ
    DIGITS = "0123456789"
    SYMBOLS = " .,!?-:;()[]{}@#$%^&*+=/\\"
    
    # ============================================
    # ПОЛНЫЙ АЛФАВИТ (ВСЕ СИМВОЛЫ)
    # ============================================
    FULL_ALPHABET = RUSSIAN_ALPHABET + RUSSIAN_ALPHABET.upper() + ENGLISH_ALPHABET + ENGLISH_ALPHABET.upper() + DIGITS + SYMBOLS
    
    # ============================================
    # КРАСИВЫЕ ЭМОДЗИ ДЛЯ ШИФРА
    # ============================================
    EMOJI_SET = [
        # Русские буквы (33 штуки)
        '🌟', '✨', '⭐', '🌙', '☀️',  # а, б, в, г, д
        '🌈', '⚡', '🔥', '💧', '🌊',  # е, ё, ж, з, и
        '❄️', '🌍', '🌎', '🌏', '🍀',  # й, к, л, м, н
        '🌸', '🌼', '🌺', '🍁', '🍂',  # о, п, р, с, т
        '🌿', '🌵', '🌴', '🍄', '🌰',  # у, ф, х, ц, ч
        '🐝', '🦋', '🐞', '🐚', '🍃',  # ш, щ, ъ, ы, ь
        '🍎', '🍐', '🍊',              # э, ю, я
        
        # Заглавные русские буквы
        '🅰️', '🅱️', '🅲', '🅳', '🅴', '🅵', '🅶', '🅷', '🅸', '🅹',
        '🅺', '🅻', '🅼', '🅽', '🅾', '🅿', '🆀', '🆁', '🆂', '🆃',
        '🆄', '🆅', '🆆', '🆇', '🆈', '🆉',
        
        # Английские буквы
        '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯',
        '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹',
        '🇺', '🇻', '🇼', '🇽', '🇾', '🇿',
        
        # Цифры
        '0️⃣', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣',
        
        # Символы
        '⬜', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '⚫', '⚪',
    ]
    
    def __init__(self, name: str = "Мой шифр"):
        self.name = name
        self.cipher_map = {}
        self.reverse_map = {}
        self.created_at = None
        self.updated_at = None
    
    # ============================================
    # ГЕНЕРАЦИЯ ШИФРА
    # ============================================
    def generate_random(self, alphabet_type: str = "russian"):
        """Автоматическая генерация шифра"""
        if alphabet_type == "russian":
            alphabet = self.RUSSIAN_ALPHABET
        else:
            alphabet = self.FULL_ALPHABET
        
        emoji_copy = self.EMOJI_SET.copy()
        random.shuffle(emoji_copy)
        
        while len(emoji_copy) < len(alphabet):
            emoji_copy.extend(self.EMOJI_SET)
        
        emoji_copy = emoji_copy[:len(alphabet)]
        
        self.cipher_map = dict(zip(alphabet, emoji_copy))
        self.reverse_map = {v: k for k, v in self.cipher_map.items()}
        return self.cipher_map
    
    # ============================================
    # РУЧНОЕ СОЗДАНИЕ ШИФРА
    # ============================================
    def create_manual_cipher(self, custom_map: Dict[str, str]) -> bool:
        """Ручное создание шифра"""
        for letter in self.RUSSIAN_ALPHABET:
            if letter not in custom_map:
                return False
        
        self.cipher_map = custom_map
        self.reverse_map = {v: k for k, v in self.cipher_map.items()}
        return True
    
    # ============================================
    # ШИФРОВАНИЕ И РАСШИФРОВКА
    # ============================================
    def encrypt(self, text: str) -> Tuple[str, List[str]]:
        """Шифрует текст"""
        result = []
        errors = []
        
        for char in text.lower():
            if char in self.cipher_map:
                result.append(self.cipher_map[char])
            else:
                result.append(char)
                errors.append(char)
        
        return ''.join(result), list(set(errors))
    
    def decrypt(self, text: str) -> Tuple[str, List[str]]:
        """Расшифровывает текст"""
        result = []
        errors = []
        i = 0
        
        while i < len(text):
            found = False
            for length in [2, 1]:
                if i + length <= len(text):
                    chunk = text[i:i+length]
                    if chunk in self.reverse_map:
                        result.append(self.reverse_map[chunk])
                        i += length
                        found = True
                        break
            
            if not found:
                result.append(text[i])
                errors.append(text[i])
                i += 1
        
        return ''.join(result), list(set(errors))
    
    # ============================================
    # ЭКСПОРТ ШИФРА (НОВАЯ ФУНКЦИЯ!)
    # ============================================
    def export_to_string(self) -> str:
        """Экспортирует шифр в строку для передачи"""
        data = {
            'name': self.name,
            'cipher_map': self.cipher_map,
            'version': '1.0'
        }
        
        json_str = json.dumps(data, ensure_ascii=False)
        encoded = base64.b64encode(json_str.encode()).decode()
        
        return f"CIPHER:{encoded}"
    
    # ============================================
    # ИМПОРТ ШИФРА (НОВАЯ ФУНКЦИЯ!)
    # ============================================
    @classmethod
    def import_from_string(cls, text: str) -> 'Cipher':
        """Импортирует шифр из строки"""
        try:
            if not text.startswith('CIPHER:'):
                return None
            
            encoded = text.replace('CIPHER:', '')
            json_str = base64.b64decode(encoded).decode()
            data = json.loads(json_str)
            
            cipher = cls(data.get('name', 'Импортированный шифр'))
            cipher.cipher_map = data.get('cipher_map', {})
            cipher.reverse_map = {v: k for k, v in cipher.cipher_map.items()}
            
            return cipher
        except:
            return None
    
    # ============================================
    # ПРЕВЬЮ ШИФРА
    # ============================================
    def get_preview(self, count: int = 10) -> str:
        """Возвращает превью шифра"""
        preview = f"📋 *{self.name}*\n\n"
        
        russian_items = [(l, self.cipher_map[l]) for l in self.RUSSIAN_ALPHABET if l in self.cipher_map]
        
        for i, (letter, emoji) in enumerate(russian_items[:count]):
            preview += f"`{letter}` → {emoji}  "
            if (i + 1) % 5 == 0:
                preview += "\n"
        
        if len(russian_items) > count:
            preview += f"\n*... и еще {len(russian_items) - count} букв*"
        
        return preview
    
    # ============================================
    # КОНВЕРТАЦИЯ В СЛОВАРЬ
    # ============================================
    def to_dict(self) -> Dict:
        """Конвертирует шифр в словарь"""
        return {
            'name': self.name,
            'cipher_map': self.cipher_map,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cipher':
        """Создает шифр из словаря"""
        cipher = cls(data.get('name', 'Без названия'))
        cipher.cipher_map = data.get('cipher_map', {})
        cipher.reverse_map = {v: k for k, v in cipher.cipher_map.items()}
        cipher.created_at = data.get('created_at')
        cipher.updated_at = data.get('updated_at')
        return cipher
