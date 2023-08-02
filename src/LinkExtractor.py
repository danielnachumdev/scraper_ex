from typing import Optional, Generator
from bs4 import BeautifulSoup as bs4
import requests


class LinkExtractor:
    TIMEOUT: float = 1

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.html: Optional[str] = None

    def get_links(self) -> Generator[str, None, None]:
        """yield the links that appear inside the page of the url one by one with repetitions
        This function is a facade for iter(self)
        Yields:
            Generator[str, None, None]: this function yield 'str' only
        """
        yield from self

    def acquire_html(self) -> None:
        try:
            response = requests.get(
                self.base_url, timeout=LinkExtractor.TIMEOUT)
            response.raise_for_status()
            self.html = response.text
        except requests.exceptions.RequestException as e:
            raise e

    def __iter__(self) -> Generator[str, None, None]:
        if self.html is None:
            raise ValueError(
                "html must be acquired first with self.acquire_html")
        soup = bs4(self.html, features="html.parser")
        for a_tag in soup.find_all("a", href=True):
            yield a_tag.attrs["href"]
