#models.py

import os
import numpy as np
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class Models:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def chat(self, message: str, system: str, model: str):
        try:
            completion = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": message}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error al generar respuesta: {e}")
            return None

    async def embedding(self, text: str, model: str = "text-embedding-3-small"):
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=model,
                dimensions=1536  # Asegurar dimensión explícita
            )
            return np.array(response.data[0].embedding, dtype=np.float32)  # Forzar float32
        except Exception as e:
            print(f"Error generando embedding: {str(e)}")
            return np.array([])