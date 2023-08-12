from queue import Queue
from typing import Optional, Any
from threading import Semaphore
# run as main module or not
if len(__name__.split(".")) == 2:
    from worker import Worker  # type:ignore # pylint: disable=import-error # noqa
else:
    import scraper.workers


class WorkerPool:
    def __init__(self, num_workers: int, worker_class: type["scraper.workers.Worker"], globals: dict) -> None:
        self.num_workers = num_workers
        self.globals: dict = globals
        self.q: Queue[tuple[Any]] = Queue()
        self.worker_class = worker_class
        self.workers: list[Worker] = []
        self.sem = Semaphore(0)

    def submit(self, obj) -> None:
        self.q.put((obj,))
        self.sem.release()

    def acquire(self) -> Optional[tuple[Any]]:
        self.sem.acquire()
        if self.q.unfinished_tasks > 0:
            return self.q.get()
        return None

    def run(self) -> None:
        for _ in range(self.num_workers):
            w = self.worker_class(self)
            w.run()
            self.workers.append(w)

    def notify(self) -> None:
        self.q.task_done()
        if self.q.unfinished_tasks <= 0:
            self.sem.release(self.num_workers)


__all__ = [
    "WorkerPool"
]
