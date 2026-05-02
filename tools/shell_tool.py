import subprocess
from typing import Dict, Any
from .base import BaseTool, ToolResult


class ShellTool(BaseTool):
    """Инструмент для выполнения shell команд (sandboxed)"""
    
    # Allowlist разрешенных команд (ограниченный набор)
    ALLOWLIST = [
        "ls", "pwd", "echo", "cat", "grep", "find", "which",
        "python", "python3", "pip", "node", "npm",
        "git", "mkdir", "touch"
    ]
    
    # Blacklist опасных операций (запрещенные паттерны)
    BLACKLIST = [
        "rm -rf /", "rm -rf ~", "rm /", "dd if=", "chmod 777",
        "sudo", "mkfs", "> /dev/sda", "curl|sh", "wget|sh"
    ]
    
    def __init__(self):
        super().__init__(
            name="shell",
            description="Выполнение shell команд (limited sandbox)"
        )
        self.dry_run = False
    
    async def execute(self, command: str, workdir: str = None, 
                     timeout: int = 30, **kwargs) -> ToolResult:
        """Выполнение команды"""
        
        # Проверка на allowlist
        if not self._is_allowed(command):
            return ToolResult(
                success=False,
                error=f"Command not allowed: {command.split()[0]}",
                metadata={"command": command}
            )
        
        # Dry-run режим
        if self.dry_run:
            return ToolResult(
                success=True,
                output=f"[DRY-RUN] Would execute: {command}",
                metadata={"dry_run": True}
            )
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=workdir
            )
            
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            
            return ToolResult(
                success=(result.returncode == 0),
                output=output,
                error=None if result.returncode == 0 else result.stderr,
                metadata={
                    "returncode": result.returncode,
                    "command": command
                }
            )
        
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Command timed out after {timeout}s",
                metadata={"timeout": timeout}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"exception": type(e).__name__}
            )
    
    def _is_allowed(self, command: str) -> bool:
        """Проверка команды по allowlist и blacklist"""
        cmd_base = command.split()[0].split('/')[-1]  # Получаем имя команды
        
        # Проверка по allowlist
        if not any(allowed in cmd_base for allowed in self.ALLOWLIST):
            return False
        
        # Проверка по blacklist (опасные паттерны)
        command_lower = command.lower()
        for forbidden in self.BLACKLIST:
            if forbidden.lower() in command_lower:
                return False
        
        return True
    
    def set_dry_run(self, enabled: bool):
        """Включение/выключение dry-run режима"""
        self.dry_run = enabled
