from threading import Thread
from abc import ABC, abstractmethod
from typing import Callable, Optional, Any
from logging import error

if len(__name__.split(".")) == 2:
    import worker_pool  # type:ignore # pylint: disable=import-error # noqa
else:
    import scraper.workers.worker_pool
Job = Callable[[], None]


class Worker(ABC):
    """A Worker Interface
    """

    def __init__(self, pool: "worker_pool.WorkerPool") -> None:
        self.pool = pool
        self.thread: Thread = Thread(target=self._loop)

    @abstractmethod
    def _work(self, *args, **kwargs) -> None:
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

    def work(self, *args, **kwargs) -> None:
        """performed the actual work that needs to happen
        execution of a single job
        """
        self._work(*args, **kwargs)
        self.notify()

    def notify(self) -> None:
        """utility method to be called on the end of each iteration of work 
        to signal actions if needed
        will call 'notification_function'
        """
        self.pool.notify()

    def acquire(self) -> Optional[tuple[Any]]:
        return self.pool.acquire()


__all__ = [
    "Worker"
]
