from threading import Thread
from abc import ABC, abstractmethod
from typing import Optional, Any
from logging import error
import scraper.workers.worker_pool  # pylint: disable=unused-import


class Worker(ABC):
    """A Worker Interface
    """

    def __init__(self, id: int, pool: "scraper.workers.worker_pool.WorkerPool") -> None:  # pylint: disable=redefined-builtin #noqa
        self.id = id
        self.pool = pool
        self.thread: Thread = Thread(target=self._loop)

    @abstractmethod
    def _work(self, obj: Any) -> None:
        """execution of a single job
        """

    def _loop(self) -> None:
        """main loop of the worker
        """
        while True:
            try:
                obj = self.acquire()
                if obj is not None:
                    self.work(obj[0])
                else:
                    break
            except Exception as e:  # pylint: disable=broad-exception-caught
                error(f"worker thread encountered an error: {e}")

    def run(self) -> None:
        """will start self._run() as a new thread with the argument given in __init__
        """
        self.thread.start()

    def is_alive(self) -> bool:
        """returns whether the worker is alive or not
        """
        return self.thread.is_alive()

    def work(self, obj: Any) -> None:
        """performed the actual work that needs to happen
        execution of a single job
        """
        self._work(obj)
        self.notify()

    def notify(self) -> None:
        """utility method to be called on the end of each iteration of work 
        to signal actions if needed
        will call 'notification_function'
        """
        self.pool._notify()  # pylint: disable=protected-access

    def acquire(self) -> Optional[tuple[Any]]:
        """acquire a new job object to work on from the pool
        will return a tuple of only one object (the job) or None if there are no more jobs
        Returns:
            Optional[tuple[Any]]: tuple of job object or None
        """
        return self.pool._acquire()  # pylint: disable=protected-access


__all__ = [
    "Worker"
]
