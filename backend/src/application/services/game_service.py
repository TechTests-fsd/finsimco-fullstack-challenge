from decimal import Decimal
from typing import Dict, List, Optional, Set

from ..ports.repositories import IGameSessionRepository, ITeamDataRepository, IApprovalRepository
from ..ports.unit_of_work import IUnitOfWork
from ..dto.session_status_dto import SessionStatusDTO, TeamDataDTO, ApprovalDTO, GameSessionDTO
from ...domain.entities.game_session import GameSession
from ...domain.entities.team_data import TeamData
from ...domain.entities.approval import Approval
from ...domain.value_objects.approval import ApprovalStatus
from ...domain.value_objects.game_type import GameType
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.services.game_configuration import GameConfiguration
from ...domain.services.valuation_calculator import ValuationCalculator


class GameService:
    """
    The main brain of the game. All the core logic lives here. It talks to the database and tells other parts of the app what to do.
    """

    def __init__(self, unit_of_work_factory):
        self._unit_of_work_factory = unit_of_work_factory
        self._valuation_calculator = ValuationCalculator()

    def create_game_session(self, session_id: str, game_type: GameType) -> GameSessionDTO:
        """Starts a new game and saves it to the database. Returns a simple data object."""
        with self._unit_of_work_factory() as uow:
            game_session = GameSession.create(session_id, game_type)
            uow.game_sessions.add(game_session)
            
            return GameSessionDTO(
                id=game_session.id,
                game_type=game_session.game_type,
                status=game_session.status,
                created_at=game_session.created_at.isoformat() if game_session.created_at else "",
                completed_at=game_session.completed_at.isoformat() if game_session.completed_at else None
            )

    def get_game_session(self, session_id: str) -> Optional[GameSession]:
        """Get game session by ID"""
        with self._unit_of_work_factory() as uow:
            return uow.game_sessions.get_by_id(session_id)

    def update_team_data(
        self, 
        session_id: str, 
        team_id: TeamId, 
        term_key: TermKey, 
        value: Decimal
    ) -> None:
        """Update team data and reset approval status"""
        with self._unit_of_work_factory() as uow:
            team_data = uow.team_data.get_by_session_and_team(session_id, team_id)
            if not team_data:
                team_data = TeamData.create(session_id, team_id, {})
            
            team_data = team_data.update_term_value(term_key, value)
            uow.team_data.save(team_data)
            
            approval = uow.approvals.get_by_session_and_term(session_id, term_key)
            if approval:
                approval = approval.reset_to_tbd()
            else:
                approval = Approval.create(session_id, term_key, ApprovalStatus.TBD)
            uow.approvals.save(approval)
            


    def toggle_approval_status(self, session_id: str, term_key: TermKey) -> ApprovalStatus:
        """Toggle approval status between TBD and OK"""
        with self._unit_of_work_factory() as uow:
            approval = uow.approvals.get_by_session_and_term(session_id, term_key)
            if not approval:
                approval = Approval.create(session_id, term_key, ApprovalStatus.TBD)
            
            approval = approval.toggle()
            uow.approvals.save(approval)
            
            return approval.status

    def get_team_data_value(
        self, 
        session_id: str, 
        team_id: TeamId, 
        term_key: TermKey
    ) -> Optional[Decimal]:
        """Get specific term value for a team"""
        with self._unit_of_work_factory() as uow:
            team_data = uow.team_data.get_by_session_and_team(session_id, team_id)
            if not team_data:
                return None
            return team_data.get_term_value(term_key)

    def get_approval_status(self, session_id: str, term_key: TermKey) -> Optional[ApprovalStatus]:
        """Get approval status for a term - returns status enum, not entity"""
        with self._unit_of_work_factory() as uow:
            approval = uow.approvals.get_by_session_and_term(session_id, term_key)
            return approval.status if approval else None

    def get_all_team_data(self, session_id: str, team_id: TeamId) -> Dict[TermKey, Decimal]:
        """Get all team data for a session"""
        with self._unit_of_work_factory() as uow:
            team_data = uow.team_data.get_by_session_and_team(session_id, team_id)
            if not team_data:
                return {}
            return team_data.term_values

    def get_all_approvals(self, session_id: str) -> Dict[TermKey, ApprovalStatus]:
        """Get all approval statuses for a session"""
        with self._unit_of_work_factory() as uow:
            approvals = uow.approvals.get_by_session(session_id)
            return {approval.term_key: approval.status for approval in approvals}

    def _calculate_game1_valuation_pure(
        self, 
        game_session, 
        team_data_dict: Dict[TeamId, TeamData], 
        approvals_dict: Dict[TermKey, Approval]
    ) -> Optional[Decimal]:
        """Сalculate Game 1 valuation from provided data"""
        if not game_session or game_session.game_type != GameType.GAME_1:
            return None
        
        required_terms = GameConfiguration.get_game_terms(GameType.GAME_1)
        
        approved_terms = {
            term_key for term_key, approval in approvals_dict.items()
            if approval.status == ApprovalStatus.OK
        }
        
        if not required_terms.issubset(approved_terms):
            return None
        
        team_data = team_data_dict.get(TeamId.TEAM_ONE)
        if not team_data:
            return None
        
        ebitda = team_data.get_term_value(TermKey.EBITDA)
        interest_rate = team_data.get_term_value(TermKey.INTEREST_RATE)
        multiple = team_data.get_term_value(TermKey.MULTIPLE)
        factor_score = team_data.get_term_value(TermKey.FACTOR_SCORE)
        
        if not all([ebitda, interest_rate, multiple, factor_score]):
            return None
        
        return self._valuation_calculator.calculate_game1_valuation(ebitda, multiple, factor_score)

    def _is_game_complete_pure(self, game_session, approvals_dict: Dict[TermKey, Approval]) -> bool:
        """Check if game is complete from provided data"""
        if not game_session:
            return False
        
        if game_session.game_type == GameType.GAME_2:
            deal_approval_terms = {
                TermKey.COMPANY1_DEAL_APPROVAL,
                TermKey.COMPANY2_DEAL_APPROVAL,
                TermKey.COMPANY3_DEAL_APPROVAL
            }
            
            approved_deal_terms = {
                term_key for term_key, approval in approvals_dict.items()
                if term_key in deal_approval_terms and approval.status == ApprovalStatus.OK
            }
            
            return deal_approval_terms.issubset(approved_deal_terms)
        else:
            required_terms = GameConfiguration.get_game_terms(game_session.game_type)
            
            approved_terms = {
                term_key for term_key, approval in approvals_dict.items()
                if approval.status == ApprovalStatus.OK
            }
            
            return required_terms.issubset(approved_terms)

    def _get_game_progress_pure(self, game_session, approvals_dict: Dict[TermKey, Approval]) -> Dict[str, int]:
        """Get game progress from provided data"""
        if not game_session:
            return {"total": 0, "approved": 0, "pending": 0}
        
        required_terms = GameConfiguration.get_game_terms(game_session.game_type)
        total_terms = len(required_terms)
        
        approved_count = sum(
            1 for approval in approvals_dict.values()
            if approval.status == ApprovalStatus.OK
        )
        
        return {
            "total": total_terms,
            "approved": approved_count,
            "pending": total_terms - approved_count
        }

    def get_session_status(self, session_id: str) -> Optional[SessionStatusDTO]:
        """
        The main 'getter'. Grabs everything about a session (data, approvals, status) and packs it into one clean object for the UI.
        """
        with self._unit_of_work_factory() as uow:
            game_session = uow.game_sessions.get_by_id(session_id)
            if not game_session:
                return None
            
            team_data_entities = {}
            for team_id in [TeamId.TEAM_ONE, TeamId.TEAM_TWO]:
                team_data_entity = uow.team_data.get_by_session_and_team(session_id, team_id)
                if team_data_entity:
                    team_data_entities[team_id] = team_data_entity
            
            approval_entities = uow.approvals.get_by_session(session_id)
            approvals_dict = {approval.term_key: approval for approval in approval_entities}
            
            valuation = None
            if game_session.game_type == GameType.GAME_1:
                valuation = self._calculate_game1_valuation_pure(game_session, team_data_entities, approvals_dict)
            
            is_complete = self._is_game_complete_pure(game_session, approvals_dict)
            progress = self._get_game_progress_pure(game_session, approvals_dict)
            
            game_session_dto = GameSessionDTO(
                id=game_session.id,
                game_type=game_session.game_type,
                status=game_session.status,
                created_at=game_session.created_at.isoformat() if game_session.created_at else "",
                completed_at=game_session.completed_at.isoformat() if game_session.completed_at else None
            )
            
            team_data_dtos = {}
            for team_id, team_data_entity in team_data_entities.items():
                team_data_dtos[team_id] = TeamDataDTO(
                    session_id=team_data_entity.session_id,
                    team_id=team_data_entity.team_id,
                    term_values=team_data_entity.term_values
                )
            
            approval_dtos = {}
            for term_key, approval in approvals_dict.items():
                approval_dtos[term_key] = ApprovalDTO(
                    session_id=approval.session_id,
                    term_key=approval.term_key,
                    status=approval.status
                )
            
            return SessionStatusDTO(
                game_session=game_session_dto,
                team_data=team_data_dtos,
                approvals=approval_dtos,
                valuation=valuation,
                is_complete=is_complete,
                progress=progress
            )

    def finalize_game2_round(self, session_id: str) -> None:
        """
        Finalize Game 2 round by creating deal approval terms.
        Validates that all input data is entered before proceeding.
        """
        with self._unit_of_work_factory() as uow:
            game_session = uow.game_sessions.get_by_id(session_id)
            if not game_session or game_session.game_type != GameType.GAME_2:
                raise ValueError("Invalid session or not Game 2")
            
            if not self._are_all_game2_inputs_filled(session_id):
                raise ValueError("Not all input data has been entered, finalization impossible")
            
            existing_approval = uow.approvals.get_by_session_and_term(session_id, TermKey.COMPANY1_DEAL_APPROVAL)
            if existing_approval:
                raise ValueError("Round already finalized")
            
            deal_approval_terms = [
                TermKey.COMPANY1_DEAL_APPROVAL,
                TermKey.COMPANY2_DEAL_APPROVAL,
                TermKey.COMPANY3_DEAL_APPROVAL
            ]
            
            for term_key in deal_approval_terms:
                approval = Approval.create(session_id, term_key, ApprovalStatus.TBD)
                uow.approvals.save(approval)
    
    def _are_all_game2_inputs_filled(self, session_id: str) -> bool:
        """A simple check to see if both teams have entered all their numbers for Game 2."""
        with self._unit_of_work_factory() as uow:
            team1_data = uow.team_data.get_by_session_and_team(session_id, TeamId.TEAM_ONE)
            team2_data = uow.team_data.get_by_session_and_team(session_id, TeamId.TEAM_TWO)
            
            if not team1_data or not team2_data:
                return False
            
            team1_required = [
                TermKey.COMPANY1_PRICE, TermKey.COMPANY1_SHARES,
                TermKey.COMPANY2_PRICE, TermKey.COMPANY2_SHARES,
                TermKey.COMPANY3_PRICE, TermKey.COMPANY3_SHARES
            ]
            
            for term_key in team1_required:
                if team1_data.get_term_value(term_key) is None:
                    return False
            
            team2_required = [
                TermKey.INVESTOR1_BID_C1, TermKey.INVESTOR1_BID_C2, TermKey.INVESTOR1_BID_C3,
                TermKey.INVESTOR2_BID_C1, TermKey.INVESTOR2_BID_C2, TermKey.INVESTOR2_BID_C3,
                TermKey.INVESTOR3_BID_C1, TermKey.INVESTOR3_BID_C2, TermKey.INVESTOR3_BID_C3
            ]
            
            for term_key in team2_required:
                if team2_data.get_term_value(term_key) is None:
                    return False
            
            return True

    def calculate_game2_summary(self, session_id: str) -> Dict:
        """
        Calculate Game 2 summary using domain service.
        GameService acts as orchestrator, not calculator.
        """
        with self._unit_of_work_factory() as uow:
            team1_data = uow.team_data.get_by_session_and_team(session_id, TeamId.TEAM_ONE)
            team2_data = uow.team_data.get_by_session_and_team(session_id, TeamId.TEAM_TWO)
            
            from ...domain.services.game2_analytics_service import Game2AnalyticsService
            
            return Game2AnalyticsService.calculate_full_summary(team1_data, team2_data)
