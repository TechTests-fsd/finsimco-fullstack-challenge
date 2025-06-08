from ..commands.toggle_approval import ToggleApprovalCommand
from ..services.game_service import GameService
from ..ports.unit_of_work import IUnitOfWork

class ToggleApprovalHandler:
    """Focused handler for approval toggle commands."""
    
    def __init__(self, game_service: GameService, unit_of_work: IUnitOfWork):
        self._game_service = game_service
        self._unit_of_work = unit_of_work
    
    def handle(self, command: ToggleApprovalCommand) -> None:
        """Handle approval toggle command within transaction."""
        with self._unit_of_work:
            self._game_service.toggle_approval(
                session_id=command.session_id,
                term_key=command.term_key,
            ) 