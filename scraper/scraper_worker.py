from threading import Lock
from queue import Queue, Empty
from logging import error
# run as main module or not
if len(__name__.split(".")) == 1:
    from worker import Worker  # type:ignore # pylint: disable=import-error # noqa
    from extractor import LinkExtractor, BaseExtractor  # type:ignore # pylint: disable=import-error # noqa
    from utils import encode_url_to_filename, LinkWrapper  # type:ignore # pylint: disable=import-error # noqa
else:
    from .worker import Worker
    from .extractor import LinkExtractor, BaseExtractor  # type:ignore # pylint: disable=import-error # noqa
    from .utils import encode_url_to_filename, LinkWrapper


class ScraperWorker(Worker):
    """An implementation for Worker which does scraping
    """

    def __init__(self, *args, **kwargs):  # pylint: disable=useless-parent-delegation
        super().__init__(*args, **kwargs)

    def _run(self, queue: Queue[LinkWrapper], unique_set: set[str], unique_set_lock: Lock,
             extract_amount: int, max_depth: int, unique: bool):
        while True:
            try:
                try:
                    # arbitrarily chosen amount of time based on the parameters so the threads wont close too early
                    lw: LinkWrapper = queue.get(
                        timeout=BaseExtractor.TIMEOUT*BaseExtractor.RETRIES)
                except Empty:
                    break
                self.work(lw, queue, unique_set, extract_amount,
                          max_depth, unique, unique_set_lock)
            except Exception as e:  # pylint: disable=broad-exception-caught
                error(f"worker thread encountered an error: {e}")

    def _work(self, lw: LinkWrapper, queue: Queue[LinkWrapper], unique_set: set[str], extract_amount: int,
              max_depth: int, unique: bool, unique_set_lock: Lock) -> None:
        """one job

        Args:
            lw (LinkWrapper): the current item
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
        extractor: BaseExtractor = LinkExtractor(lw.url)
        extractor.prepare()
        with open(f"./{lw.depth}/{filename}.html", "w", encoding="utf8") as f:
            f.write(extractor.get_data())
        if lw.depth < max_depth:
            for link in extractor.extract():
                if not (extract_count < extract_amount):  # pylint: disable=superfluous-parens
                    break
                if unique:
                    with unique_set_lock:
                        if link in unique_set:
                            continue
                        unique_set.add(link)
                extract_count += 1
                queue.put(LinkWrapper(link, lw.depth+1))
        queue.task_done()
