from typing import List
from lxml import html
from loguru import logger
from urllib.parse import urlparse, parse_qs, unquote

from mcp_server_browser.mcp_server.types import SearchResultItem

from mcp_server_browser.mcp_server.utils.extract_util import extract_text, eval_xpath_get_index


def parse_google_search_result(resp_text: str) -> List[SearchResultItem]:
    """
    使用 lxml 和您提供的精确 XPath 逻辑来解析 Google 搜索结果。
    """

    # 使用 lxml.html.fromstring 创建文档树
    dom = html.fromstring(resp_text)
    results = []

    search_results_containers = dom.xpath('.//div[contains(@jscontroller, "SC7lYd")]')

    for result in search_results_containers:
        try:
            # 提取标题
            title_tag = eval_xpath_get_index(result, './/a/h3[1]', 0, default=None)
            if title_tag is None:
                logger.debug('忽略一个结果项: 找不到标题标签 h3。')
                continue
            title = extract_text(title_tag)

            # 提取链接
            url = eval_xpath_get_index(result, './/a[h3]/@href', 0, default=None)
            if url is None:
                logger.debug(f'忽略结果项 "{title}": 找不到链接。')
                continue

            # 清洗链接
            if url.startswith('/url?q='):
                url = parse_qs(urlparse(url).query).get('q', [None])[0]
            # 提取描述内容
            content_nodes = result.xpath('.//div[div[contains(@style, "line-height")]]//span')
            # 备用选择器，参考您的 `data-sncf`
            if not content_nodes:
                content_nodes = result.xpath('.//div[contains(@data-sncf, "1")]')

            # 从内容中移除脚本标签
            for item in content_nodes:
                for script in item.xpath(".//script"):
                    script.getparent().remove(script)

            content = extract_text(content_nodes)

            results.append(SearchResultItem.model_validate({'url': unquote(url), 'title': title, 'content': content}))

        except Exception as e:
            logger.error(f"解析单个结果时出错: {e}", exc_info=True)
            continue

    return results

