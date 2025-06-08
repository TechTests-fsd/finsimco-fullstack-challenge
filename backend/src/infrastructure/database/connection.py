from sqlalchemy import create_engine, Engine
from sqlalchemy.engine import Connection
from typing import Optional
import gevent.lock

class DatabaseConnection:
    """Handles the connection to database."""
    
    def __init__(self, connection_string: str):
        self._connection_string = connection_string
        self._engine: Optional[Engine] = None
        self._engine_lock = gevent.lock.RLock()
    
    def get_engine(self) -> Engine:
        """Get SQLAlchemy engine, creating if necessary."""
        if self._engine is None:
            with self._engine_lock:
                if self._engine is None:
                    if 'sqlite' in self._connection_string:
                        from sqlalchemy.pool import StaticPool
                        self._engine = create_engine(
                            self._connection_string,
                            poolclass=StaticPool,
                            pool_pre_ping=False,
                            connect_args={"check_same_thread": False},
                            echo=False,  # Set to True for SQL debugging
                        )
                    else:
                        self._engine = create_engine(
                            self._connection_string,
                            pool_pre_ping=True,
                            pool_recycle=300,
                            echo=False,  # Set to True for SQL debugging
                        )
        return self._engine
    
    def get_connection(self) -> Connection:
        """Get new database connection."""
        return self.get_engine().connect()
    
    def close(self) -> None:
        """Close engine and all connections."""
        if self._engine:
            self._engine.dispose()
            self._engine = None
