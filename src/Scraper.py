import concurrent.futures
from threading import Lock, Thread
import os
from queue import Queue, Empty

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
    def __init__(self, num_workers: int) -> None:
        self.num_workers = num_workers

    def scrape(self, base_url: str, extract_amount: int, max_depth: int, unique: bool) -> None:
        unique_set_lock = Lock()
        # ================== SETUP ====================
        for depth in range(max_depth+1):
            if not os.path.exists(f"./{depth}"):
                os.makedirs(f"./{depth}")
        queue: Queue[LinkWrapper] = Queue()
        unique_set: set[str] = set()
        queue.put(LinkWrapper(base_url, 0))
        unique_set.add(base_url)

        def worker():
            while True:
                try:
                    should_break = self._run_one(queue, unique_set, extract_amount,
                                                 max_depth, unique, unique_set_lock)
                    if should_break:
                        break
                except Exception as e:
                    print(f"Error: {e}")

        workers = [Thread(target=worker) for _ in range(self.num_workers)]
        for w in workers:
            w.start()

        # # ================== ITERATION ====================
        # with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_workers) as executor:
        #     while not (executor._work_queue.empty() or queue.empty()):
        #         executor.submit(self._run_one, queue, unique_set, extract_amount,
        #                         max_depth, unique, unique_set_lock)

    def _run_one(self, queue: Queue[LinkWrapper], unique_set: set[str], extract_amount: int, max_depth: int, unique: bool, unique_set_lock: Lock) -> bool:
        """_summary_

        Args:
            queue (Queue[LinkWrapper]): _description_
            unique_set (set[str]): _description_
            extract_amount (int): _description_
            max_depth (int): _description_
            unique (bool): _description_
            unique_set_lock (Lock): _description_

        Returns:
            bool: whether queue was empty or not
        """
        try:
            lw: LinkWrapper = queue.get(
                timeout=LinkExtractor.TIMEOUT*LinkExtractor.RETRIES)
        except Empty:
            return True

        filename: str = encode_url_to_filename(lw.url)
        extract_count: int = 0
        extractor = LinkExtractor(lw.url)
        extractor.acquire_html()
        with open(f"./{lw.depth}/{filename}.html", "w", encoding="utf8") as f:
            f.write(extractor.html)
        for link in extractor.get_links():
            if not (extract_count < extract_amount):
                break
            if not (lw.depth < max_depth):
                continue
            if unique:
                with unique_set_lock:
                    if link in unique_set:
                        continue
                    unique_set.add(link)
            extract_count += 1
            queue.put(LinkWrapper(link, lw.depth+1))
        queue.task_done()
        return False
