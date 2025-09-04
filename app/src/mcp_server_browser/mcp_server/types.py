from typing import Optional
from pydantic import BaseModel


class BrowserNavigateToolReturn(BaseModel):
    success: bool
    message: str
    tabId: Optional[int] = None
    windowId: Optional[int] = None
    url: Optional[str] = None
    tabs: Optional[list] = None


class StructuredTabs(BaseModel):
    tabId: int
    url: str
    title: str
    active: bool


class StructuredWindows(BaseModel):
    windowId: int
    tabs: list[StructuredTabs]


class GetWindowsAndTabsToolReturn(BaseModel):
    windowCount: int
    tabCount: int
    windows: list[StructuredWindows]


class BrowserGoBackOrForwardToolReturn(BaseModel):
    success: bool
    message: str
    tabId: int
    windowId: int
    url: str


class BrowserClickElementToolReturn(BaseModel):
    success: bool
    message: str
    elementInfo: dict
    navigationOccurred: bool
    clickMethod: str


class BrowserFillOrSelectToolReturn(BaseModel):
    success: bool
    message: str
    elementInfo: dict


class BrowserGetElementsToolReturn(BaseModel):
    success: bool
    elements: list
    count: int
    query: dict


class BrowserKeyboardToolReturn(BaseModel):
    success: bool
    message: str
    targetElement: dict
    results: list


class ArticleContent(BaseModel):
    title: Optional[str]
    byline: Optional[str]
    siteName: Optional[str]
    excerpt: Optional[str]
    lang: Optional[str]


class BrowserGetWebContentToolReturn(BaseModel):
    success: bool
    url: str
    title: str
    textContent: Optional[str] = ""
    article: Optional[ArticleContent] = None
    metadata: Optional[dict] = None
    htmlContent: Optional[str] = ""


class BrowserCloseTabsToolReturn(BaseModel):
    success: bool
    message: str
    closedCount: int
    closedTabIds: list[int] = None


class BrowserScreenshot(BaseModel):
    mimeType: str
    base64Data: str


__all__ = ["BrowserNavigateToolReturn", "GetWindowsAndTabsToolReturn", "BrowserGoBackOrForwardToolReturn",
           "BrowserClickElementToolReturn", "BrowserFillOrSelectToolReturn", "BrowserGetElementsToolReturn",
           "BrowserKeyboardToolReturn", "BrowserGetWebContentToolReturn", "BrowserCloseTabsToolReturn", "BrowserScreenshot"]