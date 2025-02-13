import asyncio
import shlex
import subprocess
from dataclasses import dataclass

@dataclass
class State:
    process: subprocess.Popen | None = None

class CodeExecution:
    def __init__(self):
        self.state = State()

    async def execute(self, runtime: str, code: str):
        runtime = runtime.lower().strip()
        
        if runtime == "python":
            return await self.execute_python_code(code)
        elif runtime == "nodejs":
            return await self.execute_nodejs_code(code)
        elif runtime == "terminal":
            return await self.execute_terminal_command(code)
        elif runtime == "reset":
            return await self.reset_terminal()
        else:
            return "Error: Runtime no válido."

    async def execute_python_code(self, code: str):
        return await self.terminal_session(f"python -c {shlex.quote(code)}")

    async def execute_nodejs_code(self, code: str):
        return await self.terminal_session(f"node -e {shlex.quote(code)}")

    async def execute_terminal_command(self, command: str):
        return await self.terminal_session(command)

    async def terminal_session(self, command: str):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.state.process = process
            stdout, stderr = process.communicate()
            return stdout if stdout else stderr
        except Exception as e:
            return f"Error: {str(e)}"

    async def reset_terminal(self):
        if self.state.process:
            self.state.process.terminate()
            self.state.process = None
        return "Terminal reiniciada."