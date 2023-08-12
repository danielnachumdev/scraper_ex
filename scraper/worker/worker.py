from threading import Thread
from abc import ABC, abstractmethod
from typing import Callable

if len(__name__.split(".")) == 2:
    from extractor import Extractor  # type:ignore # pylint: disable=import-error # noqa
else:
    from ..extractor import Extractor
Job = Callable[[], None]


class Worker(ABC):
    """A Worker Interface
    """

    def __init__(self, extractor_class: Extractor, *run_args, **run_kwargs) -> None:
        self.thread: Thread = Thread(
            target=self._run, args=run_args, kwargs=run_kwargs)
        self.extractor_class = extractor_class

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
