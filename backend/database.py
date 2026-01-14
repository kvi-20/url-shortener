import datetime
import sqlite3
import logging

class DatabaseConnection:
    def __init__(self):
        self.DATABASE_NAME = "URL.db"
        self.logger=logging.getLogger(__name__)
        self.db_setup()

    def db_setup(self):
        try:
            con=sqlite3.connect(self.DATABASE_NAME)
            self.db=con.cursor()

            self.db.execute("""
                CREATE TABLE urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    long_url TEXT NOT NULL,
                    short_code VARCHAR(20) NOT NULL UNIQUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    click_count INTEGER NOT NULL DEFAULT 0
                )
            """)
        except Exception as e:
            self.logger.exception(f"[ERROR] DB creation failed: {e}")

    def insert(self, long_url: str, short_code: str):
        created_at = datetime.now(datetime.timezone.utc)
        expires_at = created_at + datetime.timedelta(minutes=5)

        query = """
            INSERT INTO urls (
                long_url,
                short_code,
                created_at,
                expires_at,
                click_count
            )
            VALUES (?, ?, ?, ?, ?)
        """

        try:
            self.db.execute(
                query,
                (
                    long_url,
                    short_code,
                    created_at,
                    expires_at,
                    0
                )
            )
            self.db.commit()
        except Exception as e:
            self.logger.exception(f"[ERROR] Insertion query failed: {e}")
            raise

    def get_short_code(self, short_code: str) -> dict:
        query = """
            SELECT long_url, expires_at
            FROM urls
            WHERE short_code = ?
        """
        try:
            cursor = self.db.execute(query, (short_code,))
            row = cursor.fetchone()

            if row is None:
                return None

            long_url, expires_at = row
            return {
                "long_url": long_url,
                "expires_at": expires_at
            }

        except Exception as e:
            self.logger.exception(f"[ERROR] query failed: {e}")
            raise

