from threading import Lock, Thread
import os
from queue import Queue, Empty
from logging import error
# run as main module or not
if len(__name__.split(".")) == 1:
    from LinkExtractor import LinkExtractor  # type:ignore # pylint: disable=import-error # noqa
    from utils import encode_url_to_filename, LinkWrapper  # type:ignore # pylint: disable=import-error # noqa
else:
    from .LinkExtractor import LinkExtractor
    from .utils import encode_url_to_filename, LinkWrapper


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

        # local implementation for easy access to upper scope
        def worker():
            # will run until it receives a "break signal"
            while True:
                try:
                    try:
                        # arbitrarily chosen amount of time based on the parameters so the threads wont close too early
                        lw: LinkWrapper = queue.get(
                            timeout=LinkExtractor.TIMEOUT*LinkExtractor.RETRIES)
                    except Empty:
                        break
                    self._run_one(lw, queue, unique_set, extract_amount,
                                  max_depth, unique, unique_set_lock)
                except Exception as e:  # pylint: disable=broad-exception-caught
                    error(f"worker thread encountered an error: {e}")

        # create workers and start them
        workers = [Thread(target=worker) for _ in range(self.num_workers)]
        for w in workers:
            w.start()

    def _run_one(self, lw: LinkWrapper, queue: Queue[LinkWrapper], unique_set: set[str], extract_amount: int,
                 max_depth: int, unique: bool, unique_set_lock: Lock) -> None:
        """one job

        Args:
            queue (Queue[LinkWrapper]): the queue to get items from
            unique_set (set[str]): the set to check uniqueness if required
            extract_amount (int): how many urls to extract from each page
            max_depth (int): the maximum depth to traverse
            unique (bool): whether to enforce uniqueness
            unique_set_lock (Lock): a synchronization lock for non atomic operations on the set
                that should be shared across all instances of this function
        """
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


__all__ = [
    "Scraper"
]
