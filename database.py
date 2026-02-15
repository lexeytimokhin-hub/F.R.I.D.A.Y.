# database.py - ПОЛНАЯ ВЕРСИЯ
import sqlite3
import json
import time
from typing import Optional, List, Dict

class Database:
    """Класс для работы с базой данных"""
    
    def __init__(self, db_name: str = 'ciphers.db'):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Инициализация таблиц"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    current_cipher_id INTEGER,
                    created_at INTEGER,
                    last_active INTEGER
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ciphers (
                    cipher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    cipher_data TEXT,
                    is_default BOOLEAN DEFAULT 0,
                    created_at INTEGER,
                    updated_at INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    cipher_id INTEGER,
                    original_text TEXT,
                    encrypted_text TEXT,
                    operation TEXT,
                    created_at INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (cipher_id) REFERENCES ciphers (cipher_id)
                )
            ''')
            
            conn.commit()
    
    def add_user(self, user_id: int, username: str = None, 
                 first_name: str = None, last_name: str = None) -> None:
        """Добавляет или обновляет пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = int(time.time())
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, created_at, last_active)
                VALUES (?, ?, ?, ?, COALESCE(
                    (SELECT created_at FROM users WHERE user_id = ?), ?
                ), ?)
            ''', (user_id, username, first_name, last_name, user_id, now, now))
            
            conn.commit()
    
    def save_cipher(self, user_id: int, cipher, is_default: bool = False) -> int:
        """Сохраняет шифр в БД"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = int(time.time())
            
            cipher_data = json.dumps(cipher.to_dict(), ensure_ascii=False)
            
            cursor.execute('''
                INSERT INTO ciphers 
                (user_id, name, cipher_data, is_default, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, cipher.name, cipher_data, is_default, now, now))
            
            cipher_id = cursor.lastrowid
            
            if is_default:
                cursor.execute('''
                    UPDATE users SET current_cipher_id = ? WHERE user_id = ?
                ''', (cipher_id, user_id))
            
            conn.commit()
            return cipher_id
    
    def get_user_ciphers(self, user_id: int) -> List[Dict]:
        """Получает все шифры пользователя"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cipher_id, name, cipher_data, is_default, created_at
                FROM ciphers
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            results = cursor.fetchall()
            ciphers = []
            
            for row in results:
                ciphers.append({
                    'id': row[0],
                    'name': row[1],
                    'data': json.loads(row[2]),
                    'is_default': bool(row[3]),
                    'created_at': row[4]
                })
            
            return ciphers
    
    def get_cipher(self, cipher_id: int) -> Optional[Dict]:
        """Получает конкретный шифр"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cipher_data FROM ciphers WHERE cipher_id = ?
            ''', (cipher_id,))
            
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            return None
    
    # ============================================
    # НОВЫЙ МЕТОД ДЛЯ ШАРИНГА
    # ============================================
    def get_cipher_by_id(self, cipher_id: int) -> Optional[Dict]:
        """Получает шифр по ID с информацией о владельце"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT c.cipher_data, u.username, u.first_name
                FROM ciphers c
                JOIN users u ON c.user_id = u.user_id
                WHERE c.cipher_id = ?
            ''', (cipher_id,))
            
            result = cursor.fetchone()
            if result:
                cipher_data = json.loads(result[0])
                cipher_data['owner_name'] = result[1] or result[2] or 'Пользователь'
                return cipher_data
            return None
    
    def set_default_cipher(self, user_id: int, cipher_id: int) -> bool:
        """Устанавливает шифр по умолчанию"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE ciphers SET is_default = 0 
                WHERE user_id = ? AND is_default = 1
            ''', (user_id,))
            
            cursor.execute('''
                UPDATE ciphers SET is_default = 1 
                WHERE cipher_id = ? AND user_id = ?
            ''', (cipher_id, user_id))
            
            cursor.execute('''
                UPDATE users SET current_cipher_id = ? 
                WHERE user_id = ?
            ''', (cipher_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_cipher(self, user_id: int, cipher_id: int) -> bool:
        """Удаляет шифр"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT current_cipher_id FROM users WHERE user_id = ?
            ''', (user_id,))
            
            current = cursor.fetchone()
            if current and current[0] == cipher_id:
                return False
            
            cursor.execute('''
                DELETE FROM ciphers 
                WHERE cipher_id = ? AND user_id = ?
            ''', (cipher_id, user_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def add_to_history(self, user_id: int, cipher_id: int, 
                       original: str, encrypted: str, operation: str) -> None:
        """Добавляет запись в историю"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            now = int(time.time())
            
            cursor.execute('''
                INSERT INTO history 
                (user_id, cipher_id, original_text, encrypted_text, operation, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, cipher_id, original, encrypted, operation, now))
            
            conn.commit()
    
    def get_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Получает историю операций"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT h.original_text, h.encrypted_text, h.operation, 
                       h.created_at, c.name
                FROM history h
                JOIN ciphers c ON h.cipher_id = c.cipher_id
                WHERE h.user_id = ?
                ORDER BY h.created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = cursor.fetchall()
            history = []
            
            for row in results:
                history.append({
                    'original': row[0],
                    'encrypted': row[1],
                    'operation': row[2],
                    'created_at': row[3],
                    'cipher_name': row[4]
                })
            
            return history
