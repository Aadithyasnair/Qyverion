from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ParserError(Exception):
    """Exception raised when a parser fails to process raw logs."""
    pass


class ParsedLog(BaseModel):
    """
    Standard model representing the structured result of any parsed log.
    Ensures consistent data structures pass downstream.
    """
    raw_data: str
    log_source: str
    severity: str
    source_ip: Optional[str] = None
    destination_ip: Optional[str] = None
    event_timestamp: datetime


class BaseParser(ABC):
    """
    Abstract Base Class that all log parsers must implement.
    Defines the contract for transforming raw string logs into structured entities.
    """
    @abstractmethod
    def parse(self, raw_data: str) -> ParsedLog:
        """
        Parses a raw string log.
        Raises ParserError if parsing is unsuccessful.
        """
        pass
