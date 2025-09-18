
from copy import deepcopy
from urllib.parse import quote_plus

from markdownify import markdownify
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Annotated

from mcp_server_browser.mcp_server.tool_util import call_tool
from mcp_server_browser.mcp_server.types import (BrowserNavigateToolReturn, GetWindowsAndTabsToolReturn,
                                                 BrowserGoBackOrForwardToolReturn,
                                                 BrowserClickElementToolReturn, BrowserFillOrSelectToolReturn,
                                                 BrowserGetElementsToolReturn,
                                                 BrowserKeyboardToolReturn, BrowserGetWebContentToolReturn,
                                                 BrowserCloseTabsToolReturn, BrowserScreenshotReturn, SearchResultItem)
from mcp_server_browser.mcp_server.utils.google_search_utils import parse_google_search_result

mcp = FastMCP("Milu", stateless_http=True)


@mcp.tool(name="browser_navigate", description="Navigate to a URL or refresh the current tab.")
async def browser_navigate(
        url: str = Field(description="URL to navigate to the website specified"),
        new_window: bool = Field(default=False, description="Create a new window to navigate to the URL or not."),
        width: int = Field(default=1280, description="Viewport width in pixels."),
        height: int = Field(default=720, description="Viewport height in pixels."),
        refresh: bool = Field(default=False,
                              description="Refresh the current active tab instead of navigating to a URL. When true, the url parameter is ignored."),
) -> BrowserNavigateToolReturn:
    result: BrowserNavigateToolReturn = await call_tool(tool_name="chrome_navigate",
                                                        tool_args={"url": url, "newWindow": new_window, "width": width,
                                                                   "height": height,
                                                                   "refresh": refresh})
    return result


@mcp.tool(name="get_windows_and_tabs", description="Get all currently open browser windows and tabs")
async def get_windows_and_tabs() -> GetWindowsAndTabsToolReturn:
    result: GetWindowsAndTabsToolReturn = await call_tool(tool_name="get_windows_and_tabs", tool_args={})
    return result


@mcp.tool(name="browser_go_back_or_forward", description="Navigate back or forward in browser history")
async def browser_go_back_or_forward(
        is_forward: bool = Field(default=False,
                                 description="Go forward in history if true, go back if false (default: false)."),
) -> BrowserGoBackOrForwardToolReturn:
    result: BrowserGoBackOrForwardToolReturn = await call_tool(tool_name="chrome_go_back_or_forward",
                                                               tool_args={"isForward": is_forward})
    return result


@mcp.tool(name="browser_click_element", description="Click on an element in the current page")
async def browser_click_element(
        selector: str = Field(description="CSS selector for the element to click. "),
) -> BrowserClickElementToolReturn:
    result: BrowserClickElementToolReturn = await call_tool(tool_name="chrome_click_element",
                                                            tool_args={"selector": selector})
    return result


@mcp.tool(name="browser_fill_or_select", description="Fill a form element or select an option with the specified value")
async def browser_fill_or_select(
        selector: str = Field(default="", description="CSS selector for the input element to fill or select"),
        value: str = Field(default="", description="Value to fill or select into the element"),
) -> BrowserFillOrSelectToolReturn:
    result: BrowserFillOrSelectToolReturn = await call_tool(tool_name="chrome_fill_or_select",
                                                            tool_args={"selector": selector, "value": value})
    return result


@mcp.tool(name="browser_get_elements", description="Get elements from the current page")
async def browser_get_elements(
        selector: str = Field(default="", description="CSS selector to filter elements."),
        target_elements: list[str] = Field(default=None, description="""
            button: 'button, input[type="button"], input[type="submit"], [role="button"]',
            link: 'a[href], [role="link"]',
            input:
              'input:not([type="button"]):not([type="submit"]):not([type="checkbox"]):not([type="radio"])',
            checkbox: 'input[type="checkbox"], [role="checkbox"]',
            radio: 'input[type="radio"], [role="radio"]',
            textarea: 'textarea',
            select: 'select',
            tab: '[role="tab"]',
            text_container: 'div, span, p, h1, h2, h3, h4, h5, h6, li',
            interactive: `[onclick], [tabindex]:not([tabindex^="-"]), [role="menuitem"], [role="slider"], [role="option"], [role="treeitem"]`,
        """),
) -> BrowserGetElementsToolReturn:
    result = await call_tool(
        tool_name="chrome_get_interactive_elements",
        tool_args={"selector": selector, "includeCoordinates": False})
    elements = []
    copy_ele = deepcopy(result.get("elements") or [])
    for element in copy_ele:
        if element.get("disabled") or not (element.get("isInteractive")):
            continue
        ele = None
        if selector:
            ele = {"selector": element["selector"], "text": element["text"]}
        elif target_elements and element.get("type") in target_elements:
            ele = {"selector": element["selector"], "text": element["text"]}
        if ele:
            elements.append(ele)
    result["elements"] = elements

    return result


@mcp.tool(name="browser_keyboard", description="Simulate keyboard events in the browser'")
async def browser_keyboard(
        keys: str = Field(description='Keys to simulate (e.g., "Enter", "Ctrl+C", "A,B,C" for sequence)'),
        selector: str = Field(description="CSS selector for the element to send keyboard events to."),
        delay: float = Field(default=0,
                             description="Delay between key sequences in milliseconds (optional, default: 0)"),
) -> BrowserKeyboardToolReturn:
    result: BrowserKeyboardToolReturn = await call_tool(tool_name="chrome_keyboard",
                                                        tool_args={"keys": keys, "selector": selector, "delay": delay})
    return result


@mcp.tool(name="browser_get_web_content", description="Fetch content from a web page")
async def browser_get_web_content(
        url: str = Field(default="",
                         description="URL to fetch content from. If not provided, uses the current active tab. In most cases, you don't need to fill in the url"),
        html_content: bool = Field(default=False,
                                   description="Get the visible HTML content of the page. If true, textContent will be ignored (default: false)"),
        text_content: bool = Field(default=True,
                                   description="Get the visible text content of the page with metadata. Ignored if htmlContent is true (default: true)"),
        selector: str = Field(default="",
                              description="CSS selector to get content from a specific element. If provided, only content from this element will be returned"),
) -> BrowserGetWebContentToolReturn:
    need_html = html_content
    need_text = text_content
    if not selector:
        need_html = True
    result: BrowserGetWebContentToolReturn = await call_tool(tool_name="chrome_get_web_content",
                                                             tool_args={"url": url, "htmlContent": need_html,
                                                                        "textContent": need_text,
                                                                        "selector": selector})
    if not html_content:
        html_text = markdownify(result["htmlContent"], strip=["a", "img"])
        result["htmlContent"] = ""
        result["textContent"] = html_text
    return result


@mcp.tool(name="browser_close_tabs", description="Close one or more browser tabs")
async def browser_close_tabs(
        tab_ids: list[int] = Field(default=None,
                                   description="Array of tab IDs to close. If not provided, will close the active tab."),
        url: str = Field(default="", description="Close tabs matching this URL. Can be used instead of tabIds."),
) -> BrowserCloseTabsToolReturn:
    result: BrowserCloseTabsToolReturn = await call_tool(tool_name="chrome_close_tabs",
                                                         tool_args={"tabIds": tab_ids or [], "url": url or ""})
    return result


@mcp.tool(name="browser_screenshot",
          description="Take a screenshot of the current page or a specific element(if you want to see the page, recommend to use chrome_get_web_content first)")
async def browser_screenshot(
        full_page: bool = Field(default=False,
                                description="Store screenshot of the entire page."),
) -> BrowserScreenshotReturn:
    result: BrowserScreenshotReturn = await call_tool(tool_name="chrome_screenshot",
                                                      tool_args={"fullPage": full_page, "storeBase64": True})
    return result


@mcp.tool(name="google_search")
async def google_search(
    query: Annotated[str, Field(
        description=(
                "The search query string. This can include advanced Google search operators. "
                "For example: '\"large language models\" filetype:pdf site:mit.edu -jobs after:2024-01-01'. "
                "Use operators like: "
                "\"exact phrase\" for exact matches, "
                "-word to exclude a word, "
                "OR for alternatives (e.g., 'deep learning OR neural network'), "
                "site: to limit to a domain, "
                "filetype: to search for a file type, "
                "after:YYYY-MM-DD or before:YYYY-MM-DD for date ranges."
        )
    )]
) -> list[SearchResultItem]:
    """
    执行 Google 高级搜索，提供精细化的查询能力。

    利用详细的筛选条件来获取高度相关的网络信息。通过组合使用各个参数，可以构建出
    复杂且精确的搜索查询，从而高效地从海量数据中定位到所需信息。

    主要特性:
    - 多维度搜索: 支持通过关键词、精确短语、排除词等多个维度进行搜索。
    - 精细化过滤: 能够按语言、地区、更新时间、网站、文件类型等进行过滤。
    - 数字范围: 支持在特定数字范围内进行搜索，适用于查找价格、年份等信息。

    """
    base_url = "https://www.google.com/search"
    encoded_query = quote_plus(query)
    final_url = f"{base_url}?q={encoded_query}"
    web_content_result: BrowserGetWebContentToolReturn = await call_tool(tool_name="chrome_get_web_content", tool_args={"url": final_url,"htmlContent": True})

    return parse_google_search_result(web_content_result["htmlContent"])