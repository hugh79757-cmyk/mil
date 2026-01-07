import sqlite3
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.init_tables()
        logger.info(f"✅ DB 연결: {db_path}")
    
    def init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rss_articles (
                id INTEGER PRIMARY KEY,
                title TEXT,
                url TEXT UNIQUE,
                source TEXT,
                published_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
