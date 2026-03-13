# smart_decrypt.py - УМНАЯ АВТОРАСШИФРОВКА
from typing import List, Dict, Any
from cipher import Cipher
from basic_ciphers import BasicCiphers, KeyboardCipher
from morse_cipher import MorseCipher
from emoji_helper import EmojiHelper

class SmartDecrypt:
    """Умная расшифровка с анализом всех методов"""
    
    def __init__(self, user_ciphers: List[Dict]):
        self.user_ciphers = user_ciphers
        self.results = []
    
    def analyze(self, text: str) -> List[Dict[str, Any]]:
        """Анализирует текст всеми возможными методами"""
        self.results = []
        
        # 1. Личные шифры пользователя
        self._check_personal_ciphers(text)
        
        # 2. Азбука Морзе
        self._check_morse(text)
        
        # 3. Раскладка клавиатуры
        self._check_keyboard_layout(text)
        
        # 4. Шифр Цезаря (все варианты сдвига)
        self._check_caesar(text)
        
        # 5. Шифр Атбаш
        self._check_atbash(text)
        
        # 6. Проверка на просто текст (без шифрования)
        self._check_plain_text(text)
        
        # Сортируем по убыванию точности
        self.results.sort(key=lambda x: x['score'], reverse=True)
        
        return self.results
    
    def _check_personal_ciphers(self, text: str):
        """Проверка личных шифров"""
        for cipher_info in self.user_ciphers:
            try:
                cipher = Cipher.from_dict(cipher_info['data'])
                decrypted, errors = cipher.decrypt(text)
                
                # Вычисляем точность
                chars = EmojiHelper.split_text_into_chars(text)
                error_chars = len(errors)
                total_chars = len(chars)
                
                if total_chars > 0:
                    score = (total_chars - error_chars) / total_chars * 100
                else:
                    score = 0
                
                # Если есть результат
                if score > 20:  # Хотя бы немного расшифровалось
                    self.results.append({
                        'type': 'personal',
                        'icon': '🔐',
                        'name': cipher_info['name'],
                        'result': decrypted,
                        'score': score,
                        'errors': errors
                    })
            except:
                continue
    
    def _check_morse(self, text: str):
        """Проверка азбуки Морзе"""
        try:
            # Очищаем текст от лишних символов для анализа
            clean_text = text.replace('/', ' / ').replace('|', ' / ')
            
            # Проверяем, похоже ли на морзянку
            morse_chars = [c for c in clean_text if c in '.-/ ']
            is_morse_like = len(morse_chars) > len(clean_text) * 0.7 if clean_text else False
            
            if is_morse_like:
                result, error = MorseCipher.morse_to_text(text)
                if result and len(result) > 0:
                    score = 90 if not error else 70
                    self.results.append({
                        'type': 'morse',
                        'icon': '⚡',
                        'name': 'Азбука Морзе',
                        'result': result,
                        'score': score,
                        'errors': [error] if error else []
                    })
        except:
            pass
    
    def _check_keyboard_layout(self, text: str):
        """Проверка раскладки клавиатуры"""
        try:
            # Пробуем оба направления
            ru_to_en = KeyboardCipher.ru_to_en(text)
            en_to_ru = KeyboardCipher.en_to_ru(text)
            
            # Анализируем результаты
            ru_words = sum(1 for c in en_to_ru if 'а' <= c <= 'я' or c == 'ё')
            en_words = sum(1 for c in ru_to_en if 'a' <= c <= 'z')
            
            total_chars = len(text.replace(' ', ''))
            
            if total_chars > 0:
                ru_score = (ru_words / total_chars) * 100 if total_chars > 0 else 0
                en_score = (en_words / total_chars) * 100 if total_chars > 0 else 0
                
                if ru_score > 50:
                    self.results.append({
                        'type': 'keyboard',
                        'icon': '⌨️',
                        'name': 'Раскладка EN→RU',
                        'result': en_to_ru,
                        'score': ru_score,
                        'errors': []
                    })
                
                if en_score > 50:
                    self.results.append({
                        'type': 'keyboard',
                        'icon': '⌨️',
                        'name': 'Раскладка RU→EN',
                        'result': ru_to_en,
                        'score': en_score,
                        'errors': []
                    })
        except:
            pass
    
    def _check_caesar(self, text: str):
        """Проверка всех вариантов Цезаря"""
        best_result = None
        best_score = 0
        best_shift = 0
        
        # Пробуем все возможные сдвиги
        for shift in range(1, 33):
            try:
                decrypted = BasicCiphers.caesar_decrypt(text, shift)
                
                # Анализируем результат
                ru_letters = sum(1 for c in decrypted if 'а' <= c <= 'я' or c == 'ё')
                en_letters = sum(1 for c in decrypted if 'a' <= c <= 'z')
                total_letters = ru_letters + en_letters
                
                words = decrypted.split()
                word_count = len(words)
                
                # Оцениваем качество
                if total_letters > 0:
                    # Проверяем наличие типичных русских слов
                    common_words = ['привет', 'как', 'что', 'это', 'код', 'бот', 'шифр']
                    common_score = sum(2 for word in common_words if word in decrypted.lower())
                    
                    score = (total_letters / max(len(decrypted), 1) * 50) + (word_count * 5) + common_score
                    
                    if score > best_score:
                        best_score = score
                        best_result = decrypted
                        best_shift = shift
            except:
                continue
        
        if best_result and best_score > 30:
            self.results.append({
                'type': 'caesar',
                'icon': '🔢',
                'name': f'Цезарь (сдвиг {best_shift})',
                'result': best_result,
                'score': min(best_score, 95),
                'errors': []
            })
    
    def _check_atbash(self, text: str):
        """Проверка шифра Атбаш"""
        try:
            decrypted = BasicCiphers.atbash_decrypt(text)
            
            # Анализируем результат
            ru_letters = sum(1 for c in decrypted if 'а' <= c <= 'я' or c == 'ё')
            total_chars = len(decrypted.replace(' ', ''))
            
            if total_chars > 0:
                score = (ru_letters / total_chars) * 100
                
                if score > 40:
                    self.results.append({
                        'type': 'atbash',
                        'icon': '🪞',
                        'name': 'Атбаш',
                        'result': decrypted,
                        'score': score,
                        'errors': []
                    })
        except:
            pass
    
    def _check_plain_text(self, text: str):
        """Проверка на обычный текст"""
        # Если текст уже похож на обычный
        ru_letters = sum(1 for c in text.lower() if 'а' <= c <= 'я' or c == 'ё')
        en_letters = sum(1 for c in text.lower() if 'a' <= c <= 'z')
        total_letters = ru_letters + en_letters
        total_chars = len(text.replace(' ', ''))
        
        if total_chars > 0 and total_letters / total_chars > 0.7:
            self.results.append({
                'type': 'plain',
                'icon': '📝',
                'name': 'Обычный текст',
                'result': text,
                'score': 50,
                'errors': []
            })
    
    def get_best_results(self, count: int = 5) -> List[Dict]:
        """Возвращает лучшие результаты"""
        return self.results[:count]
    
    def get_all_results(self) -> List[Dict]:
        """Возвращает все результаты"""
        return self.results
    
    def format_result(self, result: Dict, index: int = 1, detailed: bool = False) -> str:
        """Форматирует результат для красивого вывода"""
        medal = '🥇' if index == 1 else '🥈' if index == 2 else '🥉' if index == 3 else '📌'
        
        if detailed:
            output = f"""
{medal} *{result['icon']} {result['type'].upper()}*
┌─────────────────────
│ 📛 *Название:* {result['name']}
│ 📊 *Точность:* {result['score']:.1f}%
│ 📝 *Результат:*
│ ```
{result['result']}```
"""
            if result['errors']:
                errors_str = ', '.join(str(e) for e in result['errors'][:5])
                output += f"│ ⚠️ *Ошибки:* {errors_str}\n"
            output += "└─────────────────────"
            return output
        else:
            short_result = result['result'][:50] + '...' if len(result['result']) > 50 else result['result']
            return f"{medal} *{result['icon']} {result['name']}* — {result['score']:.1f}%\n   `{short_result}`"
