import threading
import os
from queue import Queue
import urllib.parse
import re
from .LinkExtractor import LinkExtractor


def encode_url_to_filename(url: str):
    # truncate https://
    url = url[8:]
    # remove any trailing non-alphanumeric characters
    url = re.sub(r"[^a-zA-Z0-9]$", "", url)
    # replace any non-alphanumeric characters and return
    return re.sub(r"[^a-zA-Z0-9]", "_", url)


class LinkWrapper:
    def __init__(self, url: str, depth: int):
        self.url = url
        self.depth = depth

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, LinkWrapper):
            return self.url == obj.url
        return False

    def __hash__(self) -> int:
        return hash(self.url)


class Scraper:
    @staticmethod
    def scrape(base_url: str, extract_amount: int, max_depth: int, unique: bool) -> None:
        # ================== SETUP ====================
        for depth in range(max_depth+1):
            if not os.path.exists(f"./{depth}"):
                os.makedirs(f"./{depth}")
        queue: Queue[LinkWrapper] = Queue()
        unique_set: set[str] = set()
        queue.put(LinkWrapper(base_url, 0))
        unique_set.add(base_url)

        # ================== ITERATION ====================
        while not queue.empty():
            lw: LinkWrapper = queue.get()
            filename: str = encode_url_to_filename(lw.url)
            extract_count: int = 0
            extractor = LinkExtractor(lw.url)
            extractor.acquire_html()
            with open(f"./{lw.depth}/{filename}.html", "w", encoding="utf8") as f:
                f.write(extractor.html)
            for link in extractor.get_links():
                if unique:
                    if link in unique_set:
                        continue
                    unique_set.add(link)
                if extract_count >= extract_amount:
                    continue
                extract_count += 1
                if lw.depth >= max_depth:
                    continue
                queue.put(LinkWrapper(link, lw.depth+1))
