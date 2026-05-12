import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
	email           TEXT PRIMARY KEY,
	access_token    TEXT,
	token_hash 		TEXT,
	created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
	updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

def hash(secret):
    return hashlib.sha256(secret.encode()).hexdigest()


class UserStore:
	def __init__(self, dsn):
		"""dsn is a Postgres connection string, e.g.
		'postgresql://user:pass@localhost:5432/dbname'"""
		self.conn = psycopg2.connect(dsn)
		self.conn.autocommit = True
		with self.conn.cursor() as cur:
			cur.execute(SCHEMA)
	
	def save_user(self, email, access_token, session_secret):
		"""Insert a new user, or update the token if email already exists."""
		with self.conn.cursor() as cur:
			cur.execute(
				"""
				INSERT INTO users (email, access_token,token_hash)
				VALUES (%s, %s, %s)
				ON CONFLICT (email) DO UPDATE
				SET access_token = EXCLUDED.access_token,
					token_hash = EXCLUDED.token_hash,
					updated_at = NOW()
				""",
				(email, access_token, hash(session_secret)),
			)
	
	def get_token(self, email, session_secret):
		"""Return the user row as a dict, or None if not found."""
		with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
			cur.execute("SELECT * FROM users WHERE email = %s AND token_hash = %s", (email, hash(session_secret)))
			row = cur.fetchone()
        	return row["access_token"] if row else None	

	def close(self):
		self.conn.close()