import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bot.db")


def get_connection() -> sqlite3.Connection:
	"""Returns a connection to the database."""
	return sqlite3.connect(DB_PATH)


def initialize():
	"""Creates the database tables if they don't already exist."""
	with get_connection() as conn:
		conn.execute("""
			CREATE TABLE IF NOT EXISTS voice_time (
				user_id    INTEGER PRIMARY KEY,
				seconds    REAL NOT NULL DEFAULT 0
			)
		""")
		conn.execute("""
			CREATE TABLE IF NOT EXISTS voice_time_monthly (
				user_id    INTEGER NOT NULL,
				year       INTEGER NOT NULL,
				month      INTEGER NOT NULL,
				seconds    REAL NOT NULL DEFAULT 0,
				PRIMARY KEY (user_id, year, month)
			)
		""")
		conn.commit()
	print("Database initialized")


def get_voice_time(user_id: int) -> float:
	"""Returns the total saved voice seconds for a user. Returns 0 if not found."""
	with get_connection() as conn:
		row = conn.execute(
			"SELECT seconds FROM voice_time WHERE user_id = ?", (user_id,)
		).fetchone()
	return row[0] if row else 0.0


def save_voice_time(user_id: int, seconds: float):
	"""Saves (or updates) the total voice seconds for a user."""
	with get_connection() as conn:
		conn.execute("""
			INSERT INTO voice_time (user_id, seconds)
			VALUES (?, ?)
			ON CONFLICT(user_id) DO UPDATE SET seconds = excluded.seconds
		""", (user_id, seconds))
		conn.commit()


def get_all_voice_times() -> dict[int, float]:
	"""Returns all saved voice times as a {user_id: seconds} dictionary."""
	with get_connection() as conn:
		rows = conn.execute("SELECT user_id, seconds FROM voice_time").fetchall()
	return {row[0]: row[1] for row in rows}


def save_monthly_voice_time(user_id: int, seconds: float, year: int, month: int):
	"""Saves (or updates) the monthly voice seconds for a user."""
	with get_connection() as conn:
		conn.execute("""
			INSERT INTO voice_time_monthly (user_id, year, month, seconds)
			VALUES (?, ?, ?, ?)
			ON CONFLICT(user_id, year, month) DO UPDATE SET seconds = excluded.seconds
		""", (user_id, year, month, seconds))
		conn.commit()


def get_all_monthly_voice_times(year: int, month: int) -> dict[int, float]:
	"""Returns all monthly voice times for a given year/month as a {user_id: seconds} dictionary."""
	with get_connection() as conn:
		rows = conn.execute(
			"SELECT user_id, seconds FROM voice_time_monthly WHERE year = ? AND month = ?",
			(year, month)
		).fetchall()
	return {row[0]: row[1] for row in rows}
