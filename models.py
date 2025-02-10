import os
import numpy as np
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class Models:
    async def chat(self, message: str, system: str, model: str):
        try:
            completion = await openai.ChatCompletion.acreate(
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

    async def embedding(self, input: str, model: str):
        try:
            response = await openai.Embedding.acreate(
                input=input,
                model=model
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"Error generando embedding: {e}")
            return np.array([])
