import httpx
from typing import Dict, Any
from .base import BaseTool, ToolResult


class HTTPTool(BaseTool):
    """Инструмент для HTTP запросов"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(
            name="http",
            description="Выполнение HTTP запросов"
        )
        self.timeout = timeout
        self.dry_run = False
    
    async def execute(self, method: str = "GET", url: str = "",
                     headers: Dict[str, str] = None, 
                     data: str = None, json_data: Dict = None,
                     **kwargs) -> ToolResult:
        """Выполнение HTTP запроса"""
        
        if not url:
            return ToolResult(
                success=False,
                error="URL is required",
                metadata={"method": method}
            )
        
        # Dry-run режим
        if self.dry_run:
            return ToolResult(
                success=True,
                output=f"[DRY-RUN] Would {method}: {url}",
                metadata={"dry_run": True}
            )
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                method = method.upper()
                
                if method == "GET":
                    response = await client.get(url, headers=headers)
                elif method == "POST":
                    response = await client.post(
                        url, headers=headers, 
                        content=data, json=json_data
                    )
                elif method == "PUT":
                    response = await client.put(
                        url, headers=headers,
                        content=data, json=json_data
                    )
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    return ToolResult(
                        success=False,
                        error=f"Unsupported method: {method}",
                        metadata={"method": method}
                    )
                
                return ToolResult(
                    success=(200 <= response.status_code < 300),
                    output=response.text,
                    error=None if 200 <= response.status_code < 300 else f"HTTP {response.status_code}",
                    metadata={
                        "status_code": response.status_code,
                        "headers": dict(response.headers),
                        "url": str(response.url)
                    }
                )
        
        except httpx.TimeoutException:
            return ToolResult(
                success=False,
                error=f"Request timed out after {self.timeout}s",
                metadata={"timeout": self.timeout}
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                metadata={"exception": type(e).__name__}
            )
    
    def set_dry_run(self, enabled: bool):
        """Включение/выключение dry-run режима"""
        self.dry_run = enabled
