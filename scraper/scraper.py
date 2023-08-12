from threading import Lock
import os
from typing import Optional
if len(__name__.split(".")) == 2:
    from .utils import LinkWrapper
    from .workers import WorkerPool, Worker
else:
    from utils import LinkWrapper  # type:ignore # noqa  #pylint: disable=import-error
    from workers import WorkerPool, Worker  # type:ignore # noqa  #pylint: disable=import-error


class Scraper:
    """will scrape a site according to the instructions. Doing so iteratively with multithreading

    Args:
            num_workers (int): the number of workers
            worker_class (type[Worker]): the class of the worker
            w_kwargs (Optional[dict], optional): arguments to pass to the worker's __init__. Defaults to None.
        """

    def __init__(self, num_workers: int, worker_class: type[Worker], w_kwargs: Optional[dict] = None) -> None:
        self.num_workers: int = num_workers
        self.worker_class = worker_class
        self.w_kwargs = w_kwargs if w_kwargs is not None else dict()

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
        pool = WorkerPool(self.num_workers, self.worker_class, self.w_kwargs, global_variables={
            "extract_amount": extract_amount,
            "max_depth": max_depth,
            "unique": unique,
            "unique_set": unique_set,
            "unique_set_lock": unique_set_lock
        },
        )
        pool.submit(LinkWrapper(base_url, 0))
        pool.start()


__all__ = [
    "Scraper"
]
