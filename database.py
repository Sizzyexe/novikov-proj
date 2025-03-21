import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional, Dict, Any

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    @contextmanager
    def _get_cursor(self) -> Iterator[sqlite3.Cursor]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    async def create_tables(self) -> None:
        with self._get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    current_lesson INTEGER DEFAULT 1,
                    last_active DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS lessons (
                    lesson_id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    video_file_id TEXT
                )
            ''')

    async def add_initial_lessons(self) -> None:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT 1 FROM lessons LIMIT 1')
            if not cursor.fetchone():
                lessons = [
                    (1, '', None),#'Вот твой первый урок!\nУзнаешь, как грамотно ставить цели и самое главное — достигать их! 🚀\n\nСмотри урок и начни прямо сейчас!'
                    (2, 'Подарок уже рядом!\nТы узнал, как правильно ставить цены 📈\nчтобы ты выделялся среди конкурентов, при этом сохраняя высокую маржу\n\nКак только изучишь урок до конца, нажимай на копку', None),
                ]
                cursor.executemany('''
                    INSERT INTO lessons (lesson_id, content, video_file_id)
                    VALUES (?, ?, ?)
                ''', lessons)

    async def update_lesson_video(self, lesson_id: int, file_id: str) -> None:
        with self._get_cursor() as cursor:
            cursor.execute('''
                UPDATE lessons 
                SET video_file_id = ?
                WHERE lesson_id = ?
            ''', (file_id, lesson_id))

    async def get_lesson_content(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        with self._get_cursor() as cursor:
            cursor.execute('''
                SELECT content, video_file_id 
                FROM lessons 
                WHERE lesson_id = ?
            ''', (lesson_id,))
            result = cursor.fetchone()
            return {'content': result[0], 'video_file_id': result[1]} if result else None

    async def user_exists(self, user_id: int) -> bool:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT 1 FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None
    
    async def add_user(self, user_id: int, username: str) -> None:
        with self._get_cursor() as cursor:
            cursor.execute('''
                INSERT INTO users (user_id, username) 
                VALUES (?, ?)
            ''', (user_id, username))
    
    async def get_current_lesson(self, user_id: int) -> int:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT current_lesson FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 1
    
    async def update_lesson(self, user_id: int, lesson_id: int) -> None:
        with self._get_cursor() as cursor:
            cursor.execute('''
                UPDATE users 
                SET current_lesson = ?, last_active = CURRENT_TIMESTAMP 
                WHERE user_id = ?
            ''', (lesson_id, user_id))

    async def get_total_lessons(self) -> int:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM lessons')
            return cursor.fetchone()[0]

    async def get_stats(self) -> dict:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            cursor.execute('''SELECT COUNT(*) FROM users 
                           WHERE last_active >= date('now', '-30 days')''')
            active_users = cursor.fetchone()[0]
            cursor.execute('SELECT AVG(current_lesson) FROM users')
            avg_progress = cursor.fetchone()[0] or 0
            cursor.execute('SELECT MAX(created_at) FROM users')
            last_registration = cursor.fetchone()[0] or "еще нет регистраций"
            return {
                'total_users': total_users,
                'active_users': active_users,
                'avg_progress': round(float(avg_progress), 1),
                'last_registration': last_registration
            }

    async def get_all_users(self) -> list:
        with self._get_cursor() as cursor:
            cursor.execute('SELECT user_id FROM users')
            return [row[0] for row in cursor.fetchall()]

    async def get_inactive_users(self):
        with self._get_cursor() as cursor:
            cursor.execute('''SELECT user_id FROM users 
                           WHERE last_active < date('now', '-7 days')''')
            return [row[0] for row in cursor.fetchall()]