from typing import Generator
from logging import warning

from bs4 import BeautifulSoup as bs4
import requests
# run as main module or not
if len(__name__.split(".")) == 2:
    from utils import is_valid_url, calculate_html_timeout, force_absolute_url  # type:ignore # pylint: disable=import-error # noqa
    from utils import TimeoutFunction  # type:ignore # pylint: disable=import-error # noqa
    from extractor import BaseExtractor  # type:ignore # pylint: disable=import-error # noqa
else:
    from ..utils import is_valid_url, calculate_html_timeout, force_absolute_url  # type:ignore # pylint: disable=import-error # noqa
    from ..utils import TimeoutFunction  # type:ignore # pylint: disable=import-error # noqa
    from .base_extractor import BaseExtractor


class LinkExtractor(BaseExtractor):
    """A wrapper class over bs4 to extract urls from html
    """
    # arbitrary value that should be enough but will make sure the program wont run forever and will get stuck

    def __init__(self, base_url: str, timeout_func: TimeoutFunction = calculate_html_timeout) -> None:
        super().__init__()
        self.base_url = base_url
        self._tried_to_acquire: bool = False
        self.timeout_func = timeout_func

    def _extract(self) -> Generator[str, None, None]:
        """yield the links that appear inside the page of the url one by one with repetitions
        This function is a facade for iter(self)
        Yields:
            Generator[str, None, None]: this function yield 'str' only
        """
        if self.get_data() is BaseExtractor.EMPTY_DATA:
            return
        soup = bs4(self.get_data(), features="html.parser")
        for a_tag in soup.find_all("a", href=True):
            maybe_relative_url = a_tag.attrs["href"]
            absolute_url = force_absolute_url(self.base_url, maybe_relative_url)  # noqa
            if is_valid_url(absolute_url):
                yield absolute_url

    def _prepare(self) -> str:
        """downloads the html of the base_url
        """
        self._tried_to_acquire = True
        for i in range(BaseExtractor.RETRIES):
            try:
                # we want the timeout to increase slightly with each
                # fail because maybe the call needs more time
                # but it has to be upper bounded or we risk the thread hanging
                timeout = self.timeout_func(BaseExtractor.TIMEOUT, i)
                # downloading html
                response = requests.get(self.base_url, timeout=timeout)
                # checking if it was successful or not
                response.raise_for_status()
                # if yes assign and exit the loop
                return response.text
            # if it failed try again
            except requests.exceptions.RequestException as e:
                pass
        # if completely failed notify end user
        warning(
            f"{self.base_url} Failed. Retries= {BaseExtractor.RETRIES}, Base timeout= {BaseExtractor.TIMEOUT}")
        # works well with implementation
        return ""


__all__ = [
    "LinkExtractor"
]
