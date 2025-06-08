from __future__ import annotations
from abc import ABC, abstractmethod
from types import TracebackType
from typing import Type
from sqlalchemy.engine import Connection

class IUnitOfWork(ABC):
    """
    Port for Unit of Work pattern managing transactions.
    Defines a contract for transaction management.
    NOTE: For pragmatic reasons, this port is coupled to SQLAlchemy's
    Connection object. A fully abstract implementation would define its
    own IConnection protocol, but that's an over-engineering.
    """
    
    @abstractmethod
    def get_connection(self) -> Connection:
        """Provides the active SQLAlchemy connection."""
        raise NotImplementedError
    
    def __enter__(self) -> IUnitOfWork:
        return self
    
    @abstractmethod
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None, 
        exc_tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def commit(self) -> None:
        """Commit current transaction."""
        raise NotImplementedError
    
    @abstractmethod
    def rollback(self) -> None:
        """Rollback current transaction."""
        raise NotImplementedError 