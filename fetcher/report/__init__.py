from abc import ABC, abstractmethod
from typing import Any

from .file import FileReporter
from .telegram import TelegramReporter


class Reporter(ABC):
    @abstractmethod
    def report(self, data: Any) -> None:
        """Generate a report based on the data provided."""
        pass
