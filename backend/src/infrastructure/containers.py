from dependency_injector import containers, providers
from .database.connection import DatabaseConnection
from .redis.connection import RedisConnection
from .redis.pubsub_service import PubSubService
from .database.repositories import (
    PostgreSQLGameSessionRepository,
    PostgreSQLTeamDataRepository,
    PostgreSQLApprovalRepository,
)
from .database.unit_of_work import PostgreSQLUnitOfWork
from ..application.ports.repositories import (
    IGameSessionRepository,
    ITeamDataRepository,
    IApprovalRepository,
)
from ..application.ports.unit_of_work import IUnitOfWork
from ..application.services.game_service import GameService
from ..application.handlers.update_team_data_handler import UpdateTeamDataHandler
from ..application.handlers.toggle_approval_handler import ToggleApprovalHandler

class Container(containers.DeclarativeContainer):
    """The big box of all our services. Wires everything up so we don't have to do it manually."""
    
    config = providers.Configuration()
    
    database_connection = providers.ThreadSafeSingleton(
        DatabaseConnection,
        connection_string=config.database_url,
    )
    
    redis_connection = providers.ThreadSafeSingleton(
        RedisConnection,
        redis_url=config.redis_url,
    )
    
    pubsub_service = providers.ThreadSafeSingleton(
        PubSubService,
        redis_connection=redis_connection,
    )
    
    unit_of_work = providers.Factory(
        PostgreSQLUnitOfWork,
        database_connection=database_connection,
    )
    
    
    game_service = providers.Factory(
        GameService,
        unit_of_work_factory=unit_of_work.provider,
    )
    
    update_team_data_handler = providers.Factory(
        UpdateTeamDataHandler,
        game_service=game_service,
        unit_of_work_factory=unit_of_work.provider,
    )
    
    toggle_approval_handler = providers.Factory(
        ToggleApprovalHandler,
        game_service=game_service,
        unit_of_work_factory=unit_of_work.provider,
    )
    
    @classmethod
    def create_configured(cls, database_url: str, redis_url: str ) -> 'Container':
        """A helper to create the container and jam in the config values."""
        container = cls()
        container.config.database_url.from_value(database_url)
        container.config.redis_url.from_value(redis_url)
        return container
    
    def cleanup(self) -> None:
        """Shuts down long-lived connections when the app closes."""
        for name, provider in self.providers.items():
            if isinstance(provider, providers.Singleton) and provider.is_provided():
                try:
                    instance = provider.get()
                    if hasattr(instance, 'close'):
                        instance.close()
                        logger.info(f"Cleaned up resource: {name}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup resource '{name}': {e}")