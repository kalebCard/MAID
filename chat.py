import asyncio
from agent import Agent
from memory import Memory
from helpers.tool_manager import ImportTools
from helpers.info_secure import InfoSecure

class Monologue:
    def __init__(self):
        self.agent = Agent()
        self.memory = Memory()
        self.import_tools = ImportTools()
        self.info_secure = InfoSecure()
        self.global_memory = []
        self.main_loop_active = False

    async def run(self, user_input):
        self.main_loop_active = True
        while True:
            try:
                secure_text = self.info_secure(user_input)
                normalized_text = self.agent.loop(rol="agent_normalize", goal=secure_text)
                local_memory = self.memory.retrieve(normalized_text)
                result = self.agent.loop(
                    rol="agent_rol",
                    goal=normalized_text,
                    contest=local_memory,
                    tools=self.import_tools.available_tools()
                )
                loop_memory = [user_input, secure_text, normalized_text, local_memory, result]
                self.global_memory.append(loop_memory)
                normalized_text = self.agent.loop(rol="agent_normalize", goal=loop_memory)
                self.memory.add_message(normalized_text)
                return result
            except Exception as e:
                await asyncio.sleep(0.1)
