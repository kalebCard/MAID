import aiosqlite

class AsyncDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute("PRAGMA foreign_keys = ON;")
        await self.conn.commit()

    async def execute(self, query, params=None):
        params = params or ()
        async with self.conn.execute(query, params) as cursor:
            await self.conn.commit()
            return cursor

    async def fetch(self, query, params=None):
        params = params or ()
        async with self.conn.execute(query, params) as cursor:
            return await cursor.fetchall()

    async def close(self):
        await self.conn.close()