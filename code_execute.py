import asyncio
import time
import shlex
from dataclasses import dataclass

class Tool:
    pass

class Response:
    def __init__(self, message, break_loop):
        self.message = message
        self.break_loop = break_loop

class PrintStyle:
    def __init__(self, background_color=None, font_color=None, bold=False):
        self.background_color = background_color
        self.font_color = font_color
        self.bold = bold
    def print(self, message):
        print(message)
    def stream(self, message):
        print(message, end='', flush=True)
    @staticmethod
    def error(message):
        print("ERROR:", message)

class LocalInteractiveSession:
    async def connect(self):
        pass
    def send_command(self, command):
        print(f"Ejecutando: {command}")
    async def read_output(self, timeout, reset_full_output):
        await asyncio.sleep(0.1)
        return ("Salida completa", "Salida parcial")
    def close(self):
        pass

class SSHInteractiveSession(LocalInteractiveSession):
    def __init__(self, log, addr, port, user, password):
        self.log = log
        self.addr = addr
        self.port = port
        self.user = user
        self.password = password
    async def connect(self):
        pass

class DockerContainerManager:
    def __init__(self, logger, name, image, ports, volumes):
        self.logger = logger
        self.name = name
        self.image = image
        self.ports = ports
        self.volumes = volumes
    def start_container(self):
        pass

class DummyLog:
    def update(self, content):
        pass

class DummyContext:
    def __init__(self):
        self.log = DummyLog()

class DummyAgent:
    def __init__(self):
        self.context = DummyContext()
        self.config = type("Config", (), {})()
        self.config.code_exec_docker_enabled = False
        self.config.code_exec_ssh_enabled = False
        self.config.code_exec_docker_name = "docker"
        self.config.code_exec_docker_image = "imagen"
        self.config.code_exec_docker_ports = {}
        self.config.code_exec_docker_volumes = {}
        self.config.code_exec_ssh_addr = "127.0.0.1"
        self.config.code_exec_ssh_port = 22
        self.config.code_exec_ssh_user = "usuario"
        self.config.code_exec_ssh_pass = "clave"
        self.agent_name = "Agente"
    async def handle_intervention(self):
        pass
    def get_data(self, key):
        return getattr(self, key, None)
    def set_data(self, key, value):
        setattr(self, key, value)
    def read_prompt(self, prompt, **kwargs):
        return f"{prompt} ejecutado"
    async def hist_add_tool_result(self, name, message):
        pass

class rfc_exchange:
    @staticmethod
    async def get_root_password():
        return "root"

@dataclass
class State:
    shell: any
    docker: any

class CodeExecution(Tool):
    def __init__(self, agent, args, name="CodeExecution"):
        self.agent = agent
        self.args = args
        self.name = name
        self.log = self.get_log_object()
    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        await self.prepare_state()
        runtime = self.args.get("runtime", "").lower().strip()
        if runtime == "python":
            response = await self.execute_python_code(self.args["code"])
        elif runtime == "nodejs":
            response = await self.execute_nodejs_code(self.args["code"])
        elif runtime == "terminal":
            response = await self.execute_terminal_command(self.args["code"])
        elif runtime == "output":
            response = await self.get_terminal_output(wait_with_output=5, wait_without_output=60)
        elif runtime == "reset":
            response = await self.reset_terminal()
        else:
            response = self.agent.read_prompt("fw.code_runtime_wrong.md", runtime=runtime)
        if not response:
            response = self.agent.read_prompt("fw.code_no_output.md")
        return Response(message=response, break_loop=False)
    def get_log_object(self):
        return DummyLog()
    async def after_execution(self, response, **kwargs):
        await self.agent.hist_add_tool_result(self.name, response.message)
    async def prepare_state(self, reset=False):
        state = self.agent.get_data("_cot_state")
        if not state or reset:
            if self.agent.config.code_exec_docker_enabled:
                docker = DockerContainerManager(
                    logger=self.agent.context.log,
                    name=self.agent.config.code_exec_docker_name,
                    image=self.agent.config.code_exec_docker_image,
                    ports=self.agent.config.code_exec_docker_ports,
                    volumes=self.agent.config.code_exec_docker_volumes,
                )
                docker.start_container()
            else:
                docker = None
            if self.agent.config.code_exec_ssh_enabled:
                pswd = self.agent.config.code_exec_ssh_pass or (await rfc_exchange.get_root_password())
                shell = SSHInteractiveSession(self.agent.context.log, self.agent.config.code_exec_ssh_addr, self.agent.config.code_exec_ssh_port, self.agent.config.code_exec_ssh_user, pswd)
            else:
                shell = LocalInteractiveSession()
            state = State(shell=shell, docker=docker)
            await shell.connect()
        self.agent.set_data("_cot_state", state)
        self.state = state
    async def execute_python_code(self, code, reset=False):
        escaped_code = shlex.quote(code)
        command = f"ipython -c {escaped_code}"
        return await self.terminal_session(command, reset)
    async def execute_nodejs_code(self, code, reset=False):
        escaped_code = shlex.quote(code)
        command = f"node /exe/node_eval.js {escaped_code}"
        return await self.terminal_session(command, reset)
    async def execute_terminal_command(self, command, reset=False):
        return await self.terminal_session(command, reset)
    async def terminal_session(self, command, reset=False):
        await self.agent.handle_intervention()
        for i in range(2):
            try:
                if reset:
                    await self.reset_terminal()
                self.state.shell.send_command(command)
                PrintStyle(background_color="white", font_color="#1B4F72", bold=True).print(f"{self.agent.agent_name} code execution output")
                return await self.get_terminal_output()
            except Exception as e:
                if i == 1:
                    PrintStyle.error(str(e))
                    await self.prepare_state(reset=True)
                    continue
                else:
                    raise e
    async def get_terminal_output(self, reset_full_output=True, wait_with_output=3, wait_without_output=10, max_exec_time=60):
        idle = 0
        SLEEP_TIME = 0.1
        start_time = time.time()
        full_output = ""
        while max_exec_time <= 0 or time.time() - start_time < max_exec_time:
            await asyncio.sleep(SLEEP_TIME)
            full_output, partial_output = await self.state.shell.read_output(timeout=max_exec_time, reset_full_output=reset_full_output)
            reset_full_output = False
            await self.agent.handle_intervention()
            if partial_output:
                PrintStyle(font_color="#85C1E9").stream(partial_output)
                self.log.update(full_output)
                idle = 0
            else:
                idle += 1
                if (full_output and idle > wait_with_output / SLEEP_TIME) or (not full_output and idle > wait_without_output / SLEEP_TIME):
                    break
        return full_output
    async def reset_terminal(self):
        self.state.shell.close()
        await self.prepare_state(reset=True)
        response = self.agent.read_prompt("fw.code_reset.md")
        self.log.update(response)
        return response

async def main():
    agent = DummyAgent()
    args = {"runtime": "terminal", "code": "echo 'Hola Mundo'"}
    ce = CodeExecution(agent, args)
    response = await ce.execute()
    print("Respuesta final:", response.message)

if __name__ == "__main__":
    asyncio.run(main())
