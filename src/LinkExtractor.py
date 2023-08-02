from typing import Optional, Generator
from bs4 import BeautifulSoup as bs4
import requests
import validators
from urllib.parse import urlparse, urljoin


def is_valid_url(url: str) -> bool:
    return validators.url(url) is True


class LinkExtractor:
    TIMEOUT: float = 5

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
            maybe_relative_url = a_tag.attrs["href"]
            absolute_url = LinkExtractor._make_absolute_url(
                self.base_url, maybe_relative_url)
            if is_valid_url(absolute_url):
                yield absolute_url

    @staticmethod
    def _make_absolute_url(base_url: str, url: str) -> str:
        # Parse the base URL and the given URL
        parsed_base = urlparse(base_url)
        parsed_url = urlparse(url)

        # Check if the given URL is absolute or relative
        is_absolute = bool(parsed_url.scheme) and bool(parsed_url.netloc)

        # If the URL is relative, convert it to an absolute URL using the base URL
        if not is_absolute:
            absolute_url = urljoin(base_url, url)
        else:
            absolute_url = url

        return absolute_url
