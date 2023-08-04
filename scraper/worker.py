from threading import Thread
from abc import ABC, abstractmethod
from typing import Callable

Job = Callable[[], None]


class Worker(ABC):
    """A Worker Interface
    """

    def __init__(self, *args, **kwargs) -> None:
        self.thread: Thread = Thread(
            target=self._run, args=args, kwargs=kwargs)

    @abstractmethod
    def _work(self, *args, **kwargs) -> None:
        """execution of a single job
        """

    @abstractmethod
    def _run(self, *args, **kwargs) -> None:
        """main loop of the worker
        """

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
        """
        self._work(*args, **kwargs)
