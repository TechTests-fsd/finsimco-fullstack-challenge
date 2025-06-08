from ..commands.update_team_data import UpdateTeamDataCommand
from ..services.game_service import GameService
from ..ports.unit_of_work import IUnitOfWork

class UpdateTeamDataHandler:
    """Focused handler for team data update commands."""
    
    def __init__(self, game_service: GameService, unit_of_work: IUnitOfWork):
        self._game_service = game_service
        self._unit_of_work = unit_of_work
    
    def handle(self, command: UpdateTeamDataCommand) -> None:
        """Handle team data update command within transaction."""
        with self._unit_of_work:
            self._game_service.update_team_data(
                session_id=command.session_id,
                team_id=command.team_id,
                field_name=command.field_name,
                value=command.value,
            ) 