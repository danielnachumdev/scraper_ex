from threading import Lock
import os
from .utils import LinkWrapper
from .workers import Worker, WorkerPool


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
        pool = WorkerPool(self.num_workers, self.worker_class, global_variables={
            "extract_amount": extract_amount,
            "max_depth": max_depth,
            "unique": unique,
            "unique_set": unique_set,
            "unique_set_lock": unique_set_lock
        },
        )
        pool.start()
        pool.submit(LinkWrapper(base_url, 0))


__all__ = [
    "Scraper"
]
