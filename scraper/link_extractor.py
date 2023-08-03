from typing import Generator
from logging import warning
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup as bs4
import requests
# run as main module or not
if len(__name__.split(".")) == 1:
    from utils import is_valid_url, calculate_html_timeout  # type:ignore # pylint: disable=import-error # noqa
else:
    from .utils import is_valid_url, calculate_html_timeout

# a default value which is compatible with the main logic to get desired behavior
EMPTY_HTML = ""


class LinkExtractor:
    """A wrapper class over bs4 to extract urls from html
    """
    # arbitrary value that should be enough but will make sure the program wont run forever and will get stuck
    TIMEOUT: float = 2
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
        for i in range(LinkExtractor.RETRIES):
            try:
                # we want the timeout to increase slightly with each
                # fail because maybe the call needs more time
                # but it has to be upper bounded or we risk the thread hanging
                timeout = calculate_html_timeout(LinkExtractor.TIMEOUT, i)
                # downloading html
                response = requests.get(self.base_url, timeout=timeout)
                # checking if it was successful or not
                response.raise_for_status()
                # if yes assign and exit the loop
                self.html = response.text
                return
            # if it failed try again
            except requests.exceptions.RequestException as e:
                pass
        # if completely failed notify end user
        warning(
            f"{self.base_url} Failed. Retries= {LinkExtractor.RETRIES}, Base timeout= {LinkExtractor.TIMEOUT}")

    def __iter__(self) -> Generator[str, None, None]:
        # guard block
        if self.html == EMPTY_HTML:
            if self._tried_to_acquire:
                return
            raise ValueError(
                "html must be acquired first with self.acquire_html")
        soup = bs4(self.html, features="html.parser")
        for a_tag in soup.find_all("a", href=True):
            maybe_relative_url = a_tag.attrs["href"]
            absolute_url = LinkExtractor._force_absolute_url(
                self.base_url, maybe_relative_url)
            if is_valid_url(absolute_url):
                yield absolute_url

    @staticmethod
    def _force_absolute_url(base_url: str, url: str) -> str:
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
