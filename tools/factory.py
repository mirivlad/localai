from typing import Dict, Type
from .base import BaseTool, ToolResult
from .shell_tool import ShellTool
from .filesystem_tool import FilesystemTool
from .http_tool import HTTPTool

# Опциональный импорт browser tool
try:
    from .browser_tool import BrowserTool
    BROWSER_AVAILABLE = True
except ImportError:
    BROWSER_AVAILABLE = False


class ToolFactory:
    """Фабрика для создания инструментов"""
    
    _tool_classes: Dict[str, Type[BaseTool]] = {
        "shell": ShellTool,
        "filesystem": FilesystemTool,
        "http": HTTPTool
    }
    
    if BROWSER_AVAILABLE:
        _tool_classes["browser"] = BrowserTool
    
    @classmethod
    def create_tool(cls, tool_name: str, **kwargs) -> BaseTool:
        """Создание инструмента по имени"""
        tool_class = cls._tool_classes.get(tool_name)
        if not tool_class:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return tool_class(**kwargs)
    
    @classmethod
    def register_tool(cls, name: str, tool_class: Type[BaseTool]):
        """Регистрация нового инструмента"""
        cls._tool_classes[name] = tool_class
    
    @classmethod
    def get_available_tools(cls) -> list:
        """Получение списка доступных инструментов"""
        return list(cls._tool_classes.keys())
    
    @classmethod
    def create_all_tools(cls, base_path: str = "/") -> Dict[str, BaseTool]:
        """Создание всех доступных инструментов"""
        tools = {}
        
        tools["shell"] = ShellTool()
        tools["filesystem"] = FilesystemTool(base_path=base_path)
        tools["http"] = HTTPTool()
        
        if BROWSER_AVAILABLE:
            try:
                tools["browser"] = BrowserTool()
            except:
                pass  # Если playwright не установлен
        
        return tools
