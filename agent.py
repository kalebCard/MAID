import os
from models import Models

class Agent:
    def __init__(self):
        self.models = Models()
        self.number = -1

    def load_prompt(self, rol: str):
        prompt_path = os.path.join("prompts", f"{rol}.md")
        if os.path.exists(prompt_path):
            with open(prompt_path, "r", encoding="utf-8") as file:
                return file.read()
        return ""

    async def run(self, rol: str, goal: str, contest=None, tools=None, model="chat-gpt-o-mini"):
        self.number += 1
        rol = self.load_prompt(rol)
        system = (rol, contest, tools)
        response = await self.models.chat(goal, system, model)
        self.number -= 1
        return response