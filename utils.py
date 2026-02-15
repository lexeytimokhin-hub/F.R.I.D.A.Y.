# utils.py - ПОЛНАЯ ВЕРСИЯ
import time
from datetime import datetime
from typing import Tuple
import re

def format_time(timestamp: int) -> str:
    """Форматирует timestamp в читаемую дату"""
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M")

def validate_text(text: str, max_length: int = 1000) -> Tuple[bool, str]:
    """Проверяет текст на валидность"""
    if not text:
        return False, "Текст не может быть пустым"
    
    if len(text) > max_length:
        return False, f"Текст слишком длинный (макс. {max_length} символов)"
    
    return True, "OK"

def split_long_message(text: str, max_length: int = 4000) -> list:
    """Разбивает длинное сообщение на части"""
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part)
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part)
    
    return parts

def generate_cipher_name(base_name: str = "Мой шифр") -> str:
    """Генерирует уникальное имя для шифра"""
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"{base_name} от {timestamp}"
