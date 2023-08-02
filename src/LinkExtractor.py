from typing import Optional, Generator
from bs4 import BeautifulSoup as bs4
import requests


class LinkExtractor:
    TIMEOUT: float = 1

    @staticmethod
    def download_html(url) -> Optional[str]:
        try:
            response = requests.get(url, timeout=LinkExtractor.TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error occurred: {e}")
            return None

    def __init__(self, url: str) -> None:
        self.url = url

    def __iter__(self) -> Generator[str, None, None]:
        soup = bs4(LinkExtractor.download_html(
            self.url), features="html.parser")
        for a_tag in soup.find_all("a", href=True):
            yield a_tag.attrs["href"]
