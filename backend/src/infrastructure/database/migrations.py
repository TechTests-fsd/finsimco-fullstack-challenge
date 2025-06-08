import logging
from sqlalchemy import MetaData, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from .schema import metadata

logger = logging.getLogger(__name__)

class DatabaseMigrations:
    """A simple helper to create or drop all our database tables."""
    
    def __init__(self, engine: Engine):
        self._engine = engine
    
    def create_all_tables(self) -> None:
        """Creates any tables that don't already exist in the database."""
        try:
            logger.info("Creating database tables...")
            
            inspector = inspect(self._engine)
            existing_tables = set(inspector.get_table_names())
            schema_tables = set(metadata.tables.keys())
            
            new_tables = schema_tables - existing_tables
            if new_tables:
                logger.info(f"Creating new tables: {', '.join(sorted(new_tables))}")
                metadata.create_all(self._engine, checkfirst=True)
                logger.info("Database tables created successfully")
            else:
                logger.info("All tables already exist, no changes needed")
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to create database tables: {e}")
            raise RuntimeError(f"Database migration failed: {e}") from e
    
    def drop_all_tables(self) -> None:
        """Nukes all tables. Use with caution, obviously. Good for tests."""
        try:
            logger.info("Dropping all database tables...")
            metadata.drop_all(self._engine)
            logger.info("All tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise RuntimeError(f"Database cleanup failed: {e}") from e
    
    def reset_database(self) -> None:
        """Wipes the database clean and starts over from scratch."""
        logger.info("Resetting database...")
        self.drop_all_tables()
        self.create_all_tables()
        logger.info("Database reset completed")
