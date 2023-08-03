from typing import Generator
from logging import warning
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs4
import requests
# run as main module or not
if len(__name__.split(".")) == 1:
    from utils import is_valid_url  # type:ignore # pylint: disable=import-error # noqa
else:
    from .utils import is_valid_url

EMPTY_HTML = ""


class LinkExtractor:
    """A wrapper class over bs4 to extract urls from html
    """
    # arbitrary value that should be enough but will make sure the program wont run forever and will get stuck
    TIMEOUT: float = 5
    RETRIES: int = 5

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.html: str = EMPTY_HTML
        self._tried_to_acquire: bool = False

    def get_links(self) -> Generator[str, None, None]:
        """yield the links that appear inside the page of the url one by one with repetitions
        This function is a facade for iter(self)
        Yields:
            Generator[str, None, None]: this function yield 'str' only
        """
        yield from self

    def acquire_html(self) -> None:
        """downloads the html of the base_url
        """
        self._tried_to_acquire = True
        for _ in range(LinkExtractor.RETRIES):
            try:
                response = requests.get(
                    self.base_url, timeout=LinkExtractor.TIMEOUT)
                response.raise_for_status()
                self.html = response.text
                return
            except requests.exceptions.RequestException as e:
                pass
        warning(
            f"Failed {LinkExtractor.RETRIES} times to acquire {self.base_url} after {LinkExtractor.TIMEOUT} timeout")

    def __iter__(self) -> Generator[str, None, None]:
        if self.html == EMPTY_HTML:
            if self._tried_to_acquire:
                return
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
        parsed_url = urlparse(url)

        # Check if the given URL is absolute or relative
        is_absolute = bool(parsed_url.scheme) and bool(parsed_url.netloc)

        # If the URL is relative, convert it to an absolute URL using the base URL
        if not is_absolute:
            absolute_url = urljoin(base_url, url)
        else:
            absolute_url = url

        return absolute_url


__all__ = [
    "LinkExtractor"
]
