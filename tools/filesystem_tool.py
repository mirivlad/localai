from typing import Dict, Any
from pathlib import Path
import os
from .base import BaseTool, ToolResult


class FilesystemTool(BaseTool):
    """Инструмент для работы с файловой системой"""
    
    def __init__(self, base_path: str = "/"):
        super().__init__(
            name="filesystem",
            description="Работа с файлами и директориями"
        )
        self.base_path = Path(base_path).resolve()
        self.dry_run = False
    
    async def execute(self, action: str, path: str, 
                     content: str = None, **kwargs) -> ToolResult:
        """Выполнение файловых операций"""
        
        # Нормализация пути
        target_path = self._safe_path(path)
        if not target_path:
            return ToolResult(
                success=False,
                error=f"Invalid path: {path}",
                metadata={"action": action, "path": path}
            )
        
        # Dry-run режим
        if self.dry_run:
            return ToolResult(
                success=True,
                output=f"[DRY-RUN] Would {action}: {target_path}",
                metadata={"dry_run": True}
            )
        
        try:
            if action == "read":
                return await self._read_file(target_path)
            elif action == "write":
                return await self._write_file(target_path, content)
            elif action == "list":
                return await self._list_dir(target_path)
            elif action == "exists":
                return ToolResult(
                    success=True,
                    output=str(target_path.exists()),
                    metadata={"exists": target_path.exists()}
                )
            elif action == "delete":
                return await self._delete(target_path)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown action: {action}",
                    metadata={"action": action}
                )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"exception": type(e).__name__}
            )
    
    async def _read_file(self, path: Path) -> ToolResult:
        """Чтение файла"""
        if not path.exists():
            return ToolResult(success=False, error="File not found")
        
        content = path.read_text(encoding='utf-8')
        return ToolResult(
            success=True,
            output=content,
            metadata={"size": len(content), "path": str(path)}
        )
    
    async def _write_file(self, path: Path, content: str) -> ToolResult:
        """Запись файла"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        return ToolResult(
            success=True,
            output=f"Written to {path}",
            metadata={"size": len(content), "path": str(path)}
        )
    
    async def _list_dir(self, path: Path) -> ToolResult:
        """Листинг директории"""
        if not path.exists():
            return ToolResult(success=False, error="Directory not found")
        
        entries = [str(p.name) for p in path.iterdir()]
        return ToolResult(
            success=True,
            output="\n".join(entries),
            metadata={"count": len(entries), "path": str(path)}
        )
    
    async def _delete(self, path: Path) -> ToolResult:
        """Удаление файла или директории"""
        import shutil
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return ToolResult(
            success=True,
            output=f"Deleted {path}",
            metadata={"path": str(path)}
        )
    
    def _safe_path(self, path_str: str) -> Path:
        """Проверка безопасности пути"""
        path = Path(path_str)
        
        # Если путь относительный, добавляем base_path
        if not path.is_absolute():
            path = self.base_path / path
        
        # Разрешаем только пути внутри base_path
        try:
            resolved = path.resolve()
            resolved.relative_to(self.base_path)
            return resolved
        except ValueError:
            return None
    
    def set_dry_run(self, enabled: bool):
        """Включение/выключение dry-run режима"""
        self.dry_run = enabled
