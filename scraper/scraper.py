from threading import Lock, Semaphore
import os
from queue import Queue
from typing import Any
# run as main module or not
if len(__name__.split(".")) == 1:
    from utils import LinkWrapper  # type:ignore # pylint: disable=import-error # noqa
    from workers import Worker, ScraperWorker, WorkerPool  # type:ignore # pylint: disable=import-error # noqa
    from extractors import Extractor  # type:ignore # pylint: disable=import-error # noqa
else:
    from .utils import LinkWrapper
    from .workers import Worker, ScraperWorker, WorkerPool
    from .extractors import Extractor


class Scraper:
    """will scrape a site according to the instructions. Doing so iteratively with multithreading
    """

    def __init__(self, num_workers: int, worker_class: type[Worker]) -> None:
        self.num_workers: int = num_workers
        self.worker_class: type[Worker] = worker_class

    def scrape(self, base_url: str, extract_amount: int, max_depth: int, unique: bool) -> None:
        """main entry point for logic

        Args:
            base_url (str): start url
            extract_amount (int): the number of urls to extract from each page
            max_depth (int): the maximum depth to traverse
            unique (bool): whether to force unique urls
        """
        for depth in range(max_depth+1):
            if not os.path.exists(f"./{depth}"):
                os.makedirs(f"./{depth}")
        unique_set_lock: Lock = Lock()
        unique_set: set[str] = set()
        pool = WorkerPool(self.num_workers, self.worker_class, globals={
            "extract_amount": extract_amount,
            "max_depth": max_depth,
            "unique": unique,
            "unique_set": unique_set,
            "unique_set_lock": unique_set_lock
        },
        )
        pool.run()
        pool.submit(LinkWrapper(base_url, 0))


__all__ = [
    "Scraper"
]
