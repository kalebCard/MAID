from models import Models
from memory import Memory
class Agent:
    def __init__(self):
        self.model = "gpt-4o-mini-2024-07-18"
        self.memory = Memory()
        self.models = Models()
    
    def get_tools(self):
        pass

    def start (self,num, contes, rol, tools, goal ):
        if num == -1:
            retrieve = self.memory._buscar_memoria_por_problema(goal)
            