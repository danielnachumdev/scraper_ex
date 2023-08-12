from threading import Lock
from typing import Any, cast
import scraper.workers.worker_pool  # pylint: disable=unused-import
from .worker import Worker
from ..extractors import Extractor, LinkExtractor
from ..utils import encode_url_to_filename, LinkWrapper


class ScraperWorker(Worker):
    """An implementation for Worker which does scraping
    """

    def __init__(self, pool: "scraper.workers.worker_pool.WorkerPool", extractor_class: type[Extractor]):
        super().__init__(pool)
        self.extractor_class: type[Extractor] = extractor_class

    def _work(self, obj: Any) -> None:
        """one job
        Args:
            obj (Any): the current item (actually in this case a LinkWrapper obj)
            queue (Queue[LinkWrapper]): the queue to get items from
            unique_set (set[str]): the set to check uniqueness if required
            extract_amount (int): how many urls to extract from each page
            max_depth (int): the maximum depth to traverse
            unique (bool): whether to enforce uniqueness
            unique_set_lock (Lock): a synchronization lock for non atomic operations on the set
                that should be shared across all instances of this function
        """
        lw = cast(LinkWrapper, obj)

        unique_set: set[str] = self.pool.global_variables["unique_set"]
        extract_amount: int = self.pool.global_variables["extract_amount"]
        max_depth: int = self.pool.global_variables["max_depth"]
        unique: bool = self.pool.global_variables["unique"]
        unique_set_lock: Lock = self.pool.global_variables["unique_set_lock"]

        filename: str = encode_url_to_filename(lw.url)
        extract_count: int = 0
        extractor: Extractor = self.extractor_class(lw.url)
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
                self.pool.submit(LinkWrapper(link, lw.depth+1))


__all__ = [
    "ScraperWorker"
]
