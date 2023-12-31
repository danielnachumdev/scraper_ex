from typing import Generator
from logging import warning
from bs4 import BeautifulSoup as bs4
import requests
if len(__name__.split(".")) == 3:
    from ..utils import is_valid_url, calculate_html_timeout, force_absolute_url, TimeoutFunction
    from .extractor import Extractor
else:
    from utils import is_valid_url, calculate_html_timeout, force_absolute_url, TimeoutFunction  # type:ignore # noqa  #pylint: disable=import-error
    from extractors import Extractor  # type:ignore # noqa  #pylint: disable=import-error


class LinkExtractor(Extractor):
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
        if self.get_data() is Extractor.EMPTY_DATA:
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
        for i in range(Extractor.RETRIES):
            try:
                # we want the timeout to increase slightly with each
                # fail because maybe the call needs more time
                # but it has to be upper bounded or we risk the thread hanging
                timeout = self.timeout_func(Extractor.TIMEOUT, i)
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
            f"{self.base_url} Failed. Retries= {Extractor.RETRIES}, Base timeout= {Extractor.TIMEOUT}")
        # works well with implementation
        return ""


__all__ = [
    "LinkExtractor"
]
