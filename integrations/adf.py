"""Petits constructeurs ADF (Atlassian Document Format) pour des commentaires lisibles.

ADF est le format JSON des textes riches dans Jira Cloud et Confluence Cloud.
"""


def text(value: str, bold: bool = False) -> dict:
    node = {"type": "text", "text": value}
    if bold:
        node["marks"] = [{"type": "strong"}]
    return node


def paragraph(*nodes: dict) -> dict:
    return {"type": "paragraph", "content": list(nodes)}


def heading(value: str, level: int = 4) -> dict:
    return {"type": "heading", "attrs": {"level": level}, "content": [text(value)]}


def bullet_list(items: list[list[dict]]) -> dict:
    return {
        "type": "bulletList",
        "content": [{"type": "listItem", "content": [paragraph(*item)]} for item in items],
    }


def panel(panel_type: str, *content: dict) -> dict:
    """panel_type : info, note, warning, success, error."""
    return {"type": "panel", "attrs": {"panelType": panel_type}, "content": list(content)}


def doc(*content: dict) -> dict:
    return {"type": "doc", "version": 1, "content": [c for c in content if c]}
