#memory.py

import sqlite3
import numpy as np
import faiss
import os
from models import Models
from sklearn.preprocessing import normalize

class Memory:
    def __init__(self, db_path="memory.db", faiss_path="faiss.index", embedding_model="text-embedding-3-small"):
        self.db_path = db_path
        self.faiss_path = faiss_path
        self.embedding_model = embedding_model
        self.models = Models()
        self.dimension = 1536
        self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dimension))
        self._init_db()
        self._load_faiss_index()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    embedding BLOB NOT NULL,
                    weight REAL DEFAULT 1.0
                )
                """
            )
            conn.commit()

    def _load_faiss_index(self):
        if os.path.exists(self.faiss_path):
            self.index = faiss.read_index(self.faiss_path)
        else:
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("SELECT id, embedding FROM memory").fetchall()
            embeddings = [np.frombuffer(row[1], dtype=np.float32) for row in rows]
            ids = [row[0] for row in rows]
            if embeddings:
                self.index.add_with_ids(np.array(embeddings), np.array(ids))

    def save_faiss_index(self):
        faiss.write_index(self.index, self.faiss_path)

    def _normalize_text(self, text: str) -> str:
        return text.lower().strip()

    async def _get_embedding(self, text: str) -> np.ndarray:
        emb = await self.models.embedding(text, self.embedding_model)
        if emb.size == 0:
            return np.zeros(self.dimension, dtype=np.float32)  # Usar float32
        return normalize(emb.reshape(1, -1), norm='l2')[0].astype(np.float32)  # Convertir a float32

    async def add_message(self, text: str, weight: float = 1.0) -> bool:
        embedding = await self._get_embedding(text)
        if embedding.size == 0:
            return False
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO memory (text, embedding, weight) VALUES (?, ?, ?)",
                (text, embedding.tobytes(), weight)
            )
            conn.commit()
            new_id = cursor.lastrowid
        self.index.add_with_ids(np.expand_dims(embedding, axis=0), np.array([new_id]))
        self.save_faiss_index()
        return True

    async def update_message(self, memory_id: int, new_text: str, weight: float = 1.0) -> bool:
        embedding = await self._get_embedding(new_text)
        if embedding.size == 0:
            return False
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE memory SET text = ?, embedding = ?, weight = ? WHERE id = ?",
                (new_text, embedding.tobytes(), weight, memory_id)
            )
            conn.commit()
        self._load_faiss_index()
        self.save_faiss_index()
        return True

    async def delete_message(self, memory_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM memory WHERE id = ?", (memory_id,))
            conn.commit()
        self._load_faiss_index()
        self.save_faiss_index()
        return True

    async def retrieve(self, query: str, k: int = 5, min_similarity: float = 0.0) -> list[str]:
        query_embedding = np.expand_dims(await self._get_embedding(query), axis=0)
        if query_embedding.size == 0:
            return []
        distances, indices = self.index.search(query_embedding, k)
        with sqlite3.connect(self.db_path) as conn:
            rows = {row[0]: row[1] for row in conn.execute("SELECT id, text FROM memory").fetchall()}
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in rows and dist <= min_similarity:
                results.append(rows[idx])
        return results
