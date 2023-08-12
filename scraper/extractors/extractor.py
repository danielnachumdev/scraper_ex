from abc import ABC, abstractmethod
from typing import Generator, Any


class Extractor(ABC):
    """Extractor Interface
    """
    TIMEOUT: float = 2
    RETRIES: int = 5
    EMPTY_DATA: Any = None

    def __init__(self, *args, **kwargs) -> None:  # pylint: disable=unused-argument
        self._prepared_data: Any = Extractor.EMPTY_DATA

    @abstractmethod
    def _extract(self) -> Generator[Any, None, None]:
        """Extract the items from the object

        Yields:
            Generator[Any, None, None]: items extracted by specific extractor
        """

    def extract(self,) -> Generator[Any, None, None]:
        """extracts the items

        Yields:
            Generator[Any, None, None]: generator of items
        """
        self.prepare()
        yield from self._extract()

    def is_prepared(self) -> bool:
        """return whether the data is prepared or not
        """
        return self._prepared_data is not Extractor.EMPTY_DATA

    def prepare(self) -> None:
        """Extractor preparation function to prepare before calling extract()
        """
        if not self.is_prepared():
            self._prepared_data = self._prepare()

    def get_data(self) -> Any:
        """standardization of getter
        """
        self.prepare()
        return self._prepared_data

    @abstractmethod
    def _prepare(self) -> Any:
        """does any preparation work that is nessaceary for the actual extraction
        and should return the prepared data
        """
