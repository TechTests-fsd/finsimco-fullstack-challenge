from types import TracebackType
from typing import Type, Optional
from sqlalchemy.engine import Connection
from ...application.ports.unit_of_work import IUnitOfWork
from ...application.ports.repositories import IGameSessionRepository, ITeamDataRepository, IApprovalRepository
from .connection import DatabaseConnection
from .repositories import PostgreSQLGameSessionRepository, PostgreSQLTeamDataRepository, PostgreSQLApprovalRepository


class PostgreSQLUnitOfWork(IUnitOfWork):
    """The thing that manages a single database transaction."""
    
    def __init__(self, database_connection: DatabaseConnection):
        self._database_connection = database_connection
        self._connection: Optional[Connection] = None
        self._transaction = None
        
        self.game_sessions: Optional[IGameSessionRepository] = None
        self.team_data: Optional[ITeamDataRepository] = None
        self.approvals: Optional[IApprovalRepository] = None
    
    def get_connection(self) -> Connection:
        """Get active database connection within transaction."""
        if self._connection is None:
            raise RuntimeError("UnitOfWork not entered - call within 'with' statement")
        return self._connection
    
    def __enter__(self) -> 'PostgreSQLUnitOfWork':
        """Enter transaction context."""
        self._connection = self._database_connection.get_connection()
        self._transaction = self._connection.begin()
        
        self.game_sessions = PostgreSQLGameSessionRepository(self)
        self.team_data = PostgreSQLTeamDataRepository(self)
        self.approvals = PostgreSQLApprovalRepository(self)
        
        return self
    
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException], 
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit transaction context with auto-commit/rollback."""
        try:
            if exc_type is None:
                self._transaction.commit()
            else:
                self._transaction.rollback()
        finally:
            if self._connection:
                self._connection.close()
            self._connection = None
            self._transaction = None
            
            self.game_sessions = None
            self.team_data = None
            self.approvals = None
    
    def commit(self) -> None:
        """Commit current transaction."""
        if self._transaction:
            self._transaction.commit()
    
    def rollback(self) -> None:
        """Rollback current transaction."""
        if self._transaction:
            self._transaction.rollback() 