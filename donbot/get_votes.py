from lxml.html import HtmlElement
from typing import Generator

def get_votes(post_html: HtmlElement) -> Generator[str, None, None]:
    yield ""