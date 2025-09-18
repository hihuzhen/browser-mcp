from typing import List, Union
from loguru import logger


def eval_xpath_get_index(element, xpath: str, index: int, default=None):
    """
    执行 XPath 查询并安全地获取指定索引的元素。
    对应您代码中的同名函数。
    """
    try:
        results = element.xpath(xpath)
        return results[index] if len(results) > index else default
    except Exception as e:
        logger.error(f"执行 XPath 时出错: {xpath} - {e}")
        return default


def extract_text(nodes: Union[List, object]) -> str:
    """
    从一个或多个lxml元素中提取并清理文本。
    对应您代码中的同名函数。
    """
    if not isinstance(nodes, list):
        nodes = [nodes]

    text_parts = []
    for node in nodes:
        if hasattr(node, 'text_content'):
            text_parts.append(node.text_content())
        elif isinstance(node, str):
            text_parts.append(node)

    return ' '.join(text_parts).strip()