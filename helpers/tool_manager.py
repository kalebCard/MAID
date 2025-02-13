import os
import importlib.util
import inspect
from typing import Dict, Any, List, Tuple, Optional

class ToolManager:
    def __init__(self):
        self.tools_dir = os.path.join(os.path.dirname(__file__), 'tools')
        self.tools_list = self.load_tools()
        self.cache_protocols = []

    def load_tools(self) -> Dict[str, Any]:
        tools = {}
        if not os.path.exists(self.tools_dir):
            return tools
        for filename in os.listdir(self.tools_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                tool_name = filename[:-3]
                tool_path = os.path.join(self.tools_dir, filename)
                spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    tools[tool_name] = module
        return tools

    def available_tools(self) -> List[Tuple[str, List[Tuple[str, List[str]]]]]:
        tools_available = []
        if not os.path.exists(self.tools_dir):
            return tools_available
        for filename in os.listdir(self.tools_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                tool_name = filename[:-3]
                tool_path = os.path.join(self.tools_dir, filename)
                spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    functions = []
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if obj.__module__ == tool_name:
                            for func_name, method in inspect.getmembers(obj, inspect.isfunction):
                                if func_name != '__init__':
                                    params = [p for p in inspect.signature(method).parameters if p != 'self']
                                    functions.append((func_name, params))
                    if functions:
                        tools_available.append((tool_name, functions))
        return tools_available

    def execute_protocol(self, protocol_name: str) -> Any:
        return f"Protocol '{protocol_name}' executed."

    def execute_tool(self, tool_name: str, function_name: Optional[str], parameters_function: str) -> Any:
        tool = self.tools_list.get(tool_name)
        if tool:
            class_name = tool_name.capitalize()
            tool_class = getattr(tool, class_name, None)
            if tool_class:
                instance = tool_class()
                func = getattr(instance, function_name) if function_name else getattr(instance, 'run', None)
                if func:
                    final_parameters = []
                    parameters = parameters_function.split('/*')
                    for parameter in parameters:
                        if parameter == "none":
                            final_parameters.append('')
                        elif parameter.startswith("cache "):
                            try:
                                index = int(parameter.split()[1])
                                if 0 <= index < len(self.cache_protocols):
                                    final_parameters.append(self.cache_protocols[index])
                                else:
                                    return "Index out of range."
                            except ValueError:
                                return "Index must be an integer."
                        elif parameter.startswith("protocol "):
                            protocol_name = parameter.split(' ', 1)[1]
                            result = self.execute_protocol(protocol_name)
                            final_parameters.append(result)
                        else:
                            final_parameters.append(parameter)
                    return func(*final_parameters)
                return f"Function '{function_name or 'run'}' not found in class '{class_name}'."
            return f"Class '{class_name}' not found in module '{tool_name}'."
        return f"Tool '{tool_name}' not found."
