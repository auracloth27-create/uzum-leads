from datetime import datetime, timedelta, timezone

import aiosqlite

TZ = timezone(timedelta(hours=5))  # Ташкент (UTC+5)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY,
    username       TEXT,
    language       TEXT NOT NULL DEFAULT 'ru',
    name           TEXT,
    is_uzum_seller INTEGER,
    age_range      TEXT,
    phone          TEXT,
    source         TEXT,
    completed      INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL,
    completed_at   TEXT
);
"""


def _now() -> str:
    return datetime.now(TZ).isoformat(timespec="seconds")


class Database:
    def __init__(self, path: str):
        self.path = path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute(SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

    async def get_user(self, user_id: int) -> dict | None:
        cur = await self._conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def upsert_user(
        self, user_id: int, username: str | None, language: str, source: str | None
    ) -> None:
        """Шаг 1 опросника: сохраняем язык и метку трафика (first-touch)."""
        await self._conn.execute(
            """
            INSERT INTO users (user_id, username, language, source, created_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                language = excluded.language,
                source   = COALESCE(users.source, excluded.source)
            """,
            (user_id, username, language, source, _now()),
        )
        await self._conn.commit()

    async def complete_survey(
        self,
        user_id: int,
        username: str | None,
        name: str,
        is_uzum_seller: bool,
        age_range: str,
        phone: str,
    ) -> None:
        await self._conn.execute(
            """
            UPDATE users SET username = ?, name = ?, is_uzum_seller = ?, age_range = ?,
                             phone = ?, completed = 1, completed_at = ?
            WHERE user_id = ?
            """,
            (username, name, int(is_uzum_seller), age_range, phone, _now(), user_id),
        )
        await self._conn.commit()

    async def stats(self) -> dict:
        cur = await self._conn.execute(
            """
            SELECT COUNT(*) AS total,
                   SUM(completed) AS done,
                   SUM(CASE WHEN completed = 1 AND is_uzum_seller = 1 THEN 1 ELSE 0 END) AS sellers
            FROM users
            """
        )
        row = await cur.fetchone()
        cur = await self._conn.execute(
            """
            SELECT COALESCE(source, 'direct') AS src, COUNT(*) AS started,
                   SUM(completed) AS done
            FROM users GROUP BY src ORDER BY started DESC
            """
        )
        by_source = [dict(r) for r in await cur.fetchall()]
        return {
            "total": row["total"] or 0,
            "done": row["done"] or 0,
            "sellers": row["sellers"] or 0,
            "by_source": by_source,
        }

    async def all_completed(self) -> list[dict]:
        cur = await self._conn.execute(
            "SELECT * FROM users WHERE completed = 1 ORDER BY created_at"
        )
        return [dict(r) for r in await cur.fetchall()]
