try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

from typing import Dict, Any
from .base import BaseTool, ToolResult


class BrowserTool(BaseTool):
    """Инструмент для работы с браузером через Playwright"""
    
    def __init__(self):
        super().__init__(
            name="browser",
            description="Работа с веб-страницами через браузер"
        )
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("playwright not installed. Install with: pip install playwright && playwright install")
        self.dry_run = False
    
    async def execute(self, action: str = "goto", url: str = "",
                     selector: str = None, **kwargs) -> ToolResult:
        """Выполнение браузерных действий"""
        
        if self.dry_run:
            return ToolResult(
                success=True,
                output=f"[DRY-RUN] Would {action}: {url}",
                metadata={"dry_run": True}
            )
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                if action == "goto":
                    await page.goto(url, wait_until="networkidle")
                    content = await page.content()
                    await browser.close()
                    return ToolResult(
                        success=True,
                        output=content[:5000],  # Ограничиваем размер
                        metadata={"url": url, "title": await page.title()}
                    )
                
                elif action == "screenshot":
                    await page.goto(url)
                    screenshot = await page.screenshot()
                    await browser.close()
                    return ToolResult(
                        success=True,
                        output=f"Screenshot taken: {len(screenshot)} bytes",
                        metadata={"url": url, "size": len(screenshot)}
                    )
                
                elif action == "extract":
                    await page.goto(url)
                    if selector:
                        elements = await page.query_selector_all(selector)
                        texts = [await el.inner_text() for el in elements]
                        await browser.close()
                        return ToolResult(
                            success=True,
                            output="\n".join(texts),
                            metadata={"url": url, "selector": selector, "count": len(texts)}
                        )
                    await browser.close()
                    return ToolResult(success=False, error="No selector provided")
                
                else:
                    await browser.close()
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
    
    def set_dry_run(self, enabled: bool):
        """Включение/выключение dry-run режима"""
        self.dry_run = enabled
