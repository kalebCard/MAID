from agent import Agent
from helpers.tool_manager import ToolManager

class CallSubordinate:
    def __init__(self):
        self.agent = Agent()
        self.tool_manager = ToolManager()
    
    async def create_agent(self, rol, contest, goal):
        try:
            await self.agent.loop(
                rol=rol, 
                contest=contest, 
                tools=self.tool_manager.available_tools(), 
                goal=goal
            )
        except Exception as e:
            print(f"Error: {e}")
