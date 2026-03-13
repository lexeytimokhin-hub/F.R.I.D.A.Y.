# morse_cipher.py - УЛУЧШЕННАЯ ВЕРСИЯ С ПОДДЕРЖКОЙ ЗНАКОВ
class MorseCipher:
    """Класс для работы с азбукой Морзе"""
    
    # РАСШИРЕННЫЙ СЛОВАРЬ МОРЗЕ
    MORSE_CODE = {
        # Русские буквы
        'а': '.-', 'б': '-...', 'в': '.--', 'г': '--.', 'д': '-..',
        'е': '.', 'ё': '.', 'ж': '...-', 'з': '--..', 'и': '..',
        'й': '.---', 'к': '-.-', 'л': '.-..', 'м': '--', 'н': '-.',
        'о': '---', 'п': '.--.', 'р': '.-.', 'с': '...', 'т': '-',
        'у': '..-', 'ф': '..-.', 'х': '....', 'ц': '-.-.', 'ч': '---.',
        'ш': '----', 'щ': '--.-', 'ъ': '.--.-.', 'ы': '-.--', 'ь': '-..-',
        'э': '..-..', 'ю': '..--', 'я': '.-.-',
        
        # Английские буквы
        'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.',
        'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---',
        'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---',
        'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-',
        'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--',
        'z': '--..',
        
        # Цифры
        '0': '-----', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.',
        
        # ЗНАКИ ПРЕПИНАНИЯ (РАСШИРЕННЫЙ СПИСОК)
        '.': '......',      # точка
        ',': '.-.-.-',      # запятая
        '?': '..--..',      # вопрос
        '!': '-.-.--',      # восклицание
        '-': '-....-',      # дефис
        '/': '-..-.',       # слеш
        '(': '-.--.',       # скобка (
        ')': '-.--.-',      # скобка )
        '@': '.--.-.',      # @
        ':': '---...',      # двоеточие
        ';': '-.-.-.',      # точка с запятой
        "'": '.----.',      # апостроф
        '"': '.-..-.',      # кавычки
        '=': '-...-',       # равно
        '+': '.-.-.',       # плюс
        '_': '..--.-',      # подчеркивание
        '$': '...-..-',     # доллар
        '&': '.-...',       # амперсанд
        '*': '-..-',        # звездочка
        '%': '-----',       # процент (нестандартно)
        '#': '.-...',       # решетка
        '`': '.----.',      # гравис
        '~': '.-...',       # тильда
        '|': '..--..',      # вертикальная черта
        '\\': '.-..-.',     # обратный слеш
        '^': '..--..',      # степень
        '[': '-.--.',       # скобка [
        ']': '-.--.-',      # скобка ]
        '{': '-.--.',       # скобка {
        '}': '-.--.-',      # скобка }
        '<': '.-..-.',      # меньше
        '>': '..--..',      # больше
    }
    
    # Обратный словарь
    REVERSE_MORSE = {v: k for k, v in MORSE_CODE.items()}
    
    @staticmethod
    def text_to_morse(text: str) -> str:
        """Преобразует текст в азбуку Морзе"""
        result = []
        words = text.split(' ')
        
        for word in words:
            morse_word = []
            for char in word.lower():
                if char in MorseCipher.MORSE_CODE:
                    morse_word.append(MorseCipher.MORSE_CODE[char])
                else:
                    # Пытаемся найти без учета регистра
                    char_lower = char.lower()
                    if char_lower in MorseCipher.MORSE_CODE:
                        morse_word.append(MorseCipher.MORSE_CODE[char_lower])
                    else:
                        morse_word.append('?')  # Неизвестный символ
            result.append(' '.join(morse_word))
        
        return ' / '.join(result)
    
    @staticmethod
    def morse_to_text(morse: str) -> tuple:
        """Преобразует азбуку Морзе в текст"""
        result = []
        unknown = []
        
        # Нормализуем входные данные
        morse = morse.replace('·', '.').replace('_', '-').replace('|', '/')
        morse = morse.replace('—', '-').replace('–', '-')
        
        # Разделяем на слова
        words = morse.split(' / ')
        
        for word in words:
            # Разделяем на буквы
            letters = word.split(' ')
            for letter in letters:
                if letter.strip():
                    if letter in MorseCipher.REVERSE_MORSE:
                        result.append(MorseCipher.REVERSE_MORSE[letter])
                    else:
                        # Пробуем найти без лишних пробелов
                        cleaned = letter.strip()
                        if cleaned in MorseCipher.REVERSE_MORSE:
                            result.append(MorseCipher.REVERSE_MORSE[cleaned])
                        else:
                            unknown.append(letter)
                            result.append('?')
            result.append(' ')
        
        # Убираем лишний пробел в конце
        text_result = ''.join(result).strip()
        
        if unknown:
            return text_result, f"неизвестные символы: {', '.join(set(unknown))}"
        return text_result, None
