from rich.console import Console


def fetch_announcements(url: str = None, timeout: float = None) -> dict:
    return {"announcements": [], "require_attention": False}


def display_announcements(console: Console, data: dict) -> None:
    return
