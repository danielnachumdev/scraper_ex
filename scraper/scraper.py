from threading import Lock
import os
from queue import Queue
# run as main module or not
if len(__name__.split(".")) == 1:
    from utils import LinkWrapper  # type:ignore # pylint: disable=import-error # noqa
    from worker import Worker  # type:ignore # pylint: disable=import-error # noqa
    from worker import ScraperWorker  # type:ignore # pylint: disable=import-error # noqa
else:
    from .utils import LinkWrapper
    from .worker import Worker
    from .worker import ScraperWorker


class Scraper:
    """will scrape a site according to the instructions. Doing so iteratively with multithreading
    """

    def __init__(self, num_workers: int) -> None:
        self.num_workers = num_workers

    def scrape(self, base_url: str, extract_amount: int, max_depth: int, unique: bool) -> None:
        """main entry point for logic

        Args:
            base_url (str): start url
            extract_amount (int): the number of urls to extract from each page
            max_depth (int): the maximum depth to traverse
            unique (bool): whether to force unique urls
        """
        # =========== SETUP ===========

        # main thread creates the directories for all
        for depth in range(max_depth+1):
            if not os.path.exists(f"./{depth}"):
                os.makedirs(f"./{depth}")
        # create data structures
        unique_set_lock = Lock()
        queue: Queue[LinkWrapper] = Queue()
        unique_set: set[str] = set()
        # initialize starter values
        queue.put(LinkWrapper(base_url, 0))
        unique_set.add(base_url)

        # create workers and start them
        workers: set[Worker] = set([
            ScraperWorker(
                queue,
                unique_set,
                unique_set_lock,
                extract_amount,
                max_depth,
                unique
            )
            for _ in range(self.num_workers)
        ])

        # ========== INITIAL RUN ==========
        for w in workers:
            w.run()

        # ============ AUTO-SCALING ==============
        while queue.unfinished_tasks > 0:
            to_remove = set()
            for w in workers:
                if not w.is_alive():
                    to_remove.add(w)
            workers.difference_update(to_remove)

            maximum_allowed = min(queue.unfinished_tasks, self.num_workers)
            if len(workers) < maximum_allowed:
                for _ in range(maximum_allowed-len(workers)):
                    w = ScraperWorker(queue, unique_set, extract_amount,
                                      max_depth, unique, unique_set_lock)
                    w.run()
                    workers.add(w)


__all__ = [
    "Scraper"
]
