
import secrets
from datetime import datetime, timedelta, timezone

from psycopg2.extras import RealDictCursor


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
	session_token    TEXT PRIMARY KEY,
	email            TEXT NOT NULL REFERENCES users(email) ON DELETE CASCADE,
	expires_at       TIMESTAMPTZ NOT NULL,
	created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS sessions_email_idx ON sessions (email);
CREATE INDEX IF NOT EXISTS sessions_expires_at_idx ON sessions (expires_at);
"""


# Default lifetime — 7 days. Refresh by issuing a new session on activity,
# or just let the user log in again with OTP.
DEFAULT_TTL = timedelta(days=7)


class SessionStore:
	def __init__(self, pool):
		"""
		Takes the same psycopg2 connection pool that UserBase uses.
		Both stores share one pool so we don't waste DB connections.
		"""
		self.pool = pool
		conn = self.pool.getconn()
		try:
			conn.autocommit = True
			with conn.cursor() as cur:
				cur.execute(SCHEMA)
		finally:
			self.pool.putconn(conn)
	
	def _with_conn(self, fn):
		conn = self.pool.getconn()
		try:
			conn.autocommit = True
			return fn(conn)
		finally:
			self.pool.putconn(conn)
	
	def create_session(self, email, ttl=DEFAULT_TTL):
		"""Generate a new session token for this email. Returns the token."""
		token = secrets.token_urlsafe(32)
		expires_at = datetime.now(timezone.utc) + ttl
		
		def op(conn):
			with conn.cursor() as cur:
				cur.execute(
					"""
					INSERT INTO sessions (session_token, email, expires_at)
					VALUES (%s, %s, %s)
					""",
					(token, email, expires_at),
				)
		self._with_conn(op)
		return token
	
	def get_email_for_session(self, token):
		"""
		Returns the email associated with this session token, or None if
		the token doesn't exist or has expired.
		"""
		def op(conn):
			with conn.cursor(cursor_factory=RealDictCursor) as cur:
				cur.execute(
					"""
					SELECT email FROM sessions
					WHERE session_token = %s
					  AND expires_at > NOW()
					""",
					(token,),
				)
				row = cur.fetchone()
				return row["email"] if row else None
		return self._with_conn(op)
	
	def delete_session(self, token):
		"""Logout: invalidate this session immediately."""
		def op(conn):
			with conn.cursor() as cur:
				cur.execute(
					"DELETE FROM sessions WHERE session_token = %s",
					(token,),
				)
		self._with_conn(op)
	
	def delete_expired(self):
		"""Cleanup: remove all expired sessions. Call from a cron job."""
		def op(conn):
			with conn.cursor() as cur:
				cur.execute("DELETE FROM sessions WHERE expires_at <= NOW()")
		self._with_conn(op)