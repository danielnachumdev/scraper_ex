import re
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


__alL__ = [
    "encode_url_to_filename",
    "is_valid_url",
    "LinkWrapper"
]
