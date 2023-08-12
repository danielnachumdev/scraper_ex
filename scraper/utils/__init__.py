import re
from typing import Callable
from urllib.parse import urlparse, urljoin
import validators  # type:ignore


def encode_url_to_filename(url: str) -> str:
    """parses the url to a valid filename

    Args:
        url (str): url to parse

    Returns:
        str: the valid filename version of the url 
    """
    # truncate https://
    url = url[8:]
    # remove any trailing non-alphanumeric characters
    url = re.sub(r"[^a-zA-Z0-9]$", "", url)
    # replace any non-alphanumeric characters and return
    return re.sub(r"[^a-zA-Z0-9]", "_", url)


def is_valid_url(string: str) -> bool:
    """returns true if a given string is a valid url address
    """
    return validators.url(string) is True


class LinkWrapper:
    """A small wrapper class for the url and the depth of it to assign meaning to the values
    """

    def __init__(self, url: str, depth: int):
        self.url = url
        self.depth = depth

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, LinkWrapper):
            return self.url == obj.url
        return False

    def __hash__(self) -> int:
        return hash(self.url)


def calculate_html_timeout(base_timeout: float, try_number: int) -> float:
    """will create a slightly increasing but upper bounded value 
    for the timeout with respect to the number of tries

    Args:
        base_timeout (float): base timeout to calculate with respect to it
        try_number (int): the index of the current trial number

    Raises:
        ValueError: if try_number is has a negative value

    Returns:
        float: new timeout value
    """
    if try_number < 0:
        raise ValueError("try_number must be a non-negative integer")
    return base_timeout + base_timeout*1/(try_number+1)


def force_absolute_url(base_url: str, url: str) -> str:
    """forces a url to be absolute

    Args:
        base_url (str): a base url
        url (str): a maybe relative url to base url

    Returns:
        str: the absolute version of the url
    """
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


TimeoutFunction = Callable[[float, int], float]

__alL__ = [
    "encode_url_to_filename",
    "is_valid_url",
    "LinkWrapper",
    "calculate_html_timeout",
    "force_absolute_url",
    "TimeoutFunction"
]
