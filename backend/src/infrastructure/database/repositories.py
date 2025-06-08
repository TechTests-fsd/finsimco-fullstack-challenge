from typing import List, Optional, Dict
from uuid import uuid4
from sqlalchemy import select, insert, update, delete
from ...application.ports.repositories import (
    IGameSessionRepository, 
    ITeamDataRepository, 
    IApprovalRepository
)
from ...application.ports.unit_of_work import IUnitOfWork
from ...domain.entities.game_session import GameSession
from ...domain.entities.team_data import TeamData
from ...domain.entities.approval import Approval
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from .schema import game_sessions, team_data, approval_status

class PostgreSQLGameSessionRepository(IGameSessionRepository):
    """Handles reading and writing the key-value data for each team."""
    
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work
    
    def add(self, session: GameSession) -> None:
        """Save new game session."""
        conn = self._unit_of_work.get_connection()
        
        stmt = insert(game_sessions).values(
            id=session.id,
            game_type=session.game_type,
            status=session.status,
            created_at=session.created_at,
            completed_at=session.completed_at,
        )
        conn.execute(stmt)

    def save(self, session: GameSession) -> None:
        """Update existing game session."""
        conn = self._unit_of_work.get_connection()
        
        stmt = update(game_sessions).where(
            game_sessions.c.id == session.id
        ).values(
            status=session.status,
            completed_at=session.completed_at,
        )
        conn.execute(stmt)
    
    def get_by_id(self, session_id: str) -> Optional[GameSession]:
        """Find session by ID."""
        conn = self._unit_of_work.get_connection()
        
        stmt = select(game_sessions).where(game_sessions.c.id == session_id)
        result = conn.execute(stmt).fetchone()
        
        if not result:
            return None
            
        return GameSession(
            id=result.id,
            game_type=result.game_type,
            status=result.status,
            created_at=result.created_at,
            completed_at=result.completed_at,
        )
    
    def get_active_sessions(self) -> List[GameSession]:
        """Find active sessions."""
        conn = self._unit_of_work.get_connection()
        
        stmt = select(game_sessions).where(
            game_sessions.c.status == 'active'
        )
        results = conn.execute(stmt).fetchall()
        
        return [
            GameSession(
                id=row.id,
                game_type=row.game_type,
                status=row.status,
                created_at=row.created_at,
                completed_at=row.completed_at,
            ) for row in results
        ]

class PostgreSQLTeamDataRepository(ITeamDataRepository):
    """PostgreSQL implementation of team data repository."""
    
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work
    
    def save(self, team_data_entity: TeamData) -> None:
        """Save team data."""
        conn = self._unit_of_work.get_connection()
        
        for term_key, value in team_data_entity.term_values.items():
            check_stmt = select(team_data).where(
                (team_data.c.session_id == team_data_entity.session_id) &
                (team_data.c.team_id == team_data_entity.team_id.value) &
                (team_data.c.term_key == term_key.value)
            )
            existing = conn.execute(check_stmt).fetchone()
            
            if existing:
                update_stmt = update(team_data).where(
                    (team_data.c.session_id == team_data_entity.session_id) &
                    (team_data.c.team_id == team_data_entity.team_id.value) &
                    (team_data.c.term_key == term_key.value)
                ).values(value=value)
                conn.execute(update_stmt)
            else:
                insert_stmt = insert(team_data).values(
                    id=str(uuid4()),
                    session_id=team_data_entity.session_id,
                    team_id=team_data_entity.team_id.value,
                    term_key=term_key.value,
                    value=value,
                )
                conn.execute(insert_stmt)
    
    def get_by_session_and_team(self, session_id: str, team_id: TeamId) -> Optional[TeamData]:
        """Find team data by session and team."""
        conn = self._unit_of_work.get_connection()
        
        stmt = select(team_data).where(
            (team_data.c.session_id == session_id) &
            (team_data.c.team_id == team_id.value)
        )
        results = conn.execute(stmt).fetchall()
        
        if not results:
            return None
        
        term_values = {}
        for row in results:
            term_key = TermKey(row.term_key)
            term_values[term_key] = row.value
            
        return TeamData.create(session_id, team_id, term_values)
    
    def get_by_session(self, session_id: str) -> Dict[TeamId, TeamData]:
        """Find all team data for a session."""
        conn = self._unit_of_work.get_connection()
        
        stmt = select(team_data).where(team_data.c.session_id == session_id)
        results = conn.execute(stmt).fetchall()
        
        teams_data = {}
        for row in results:
            team_id = TeamId(row.team_id)
            if team_id not in teams_data:
                teams_data[team_id] = {}
            
            term_key = TermKey(row.term_key)
            teams_data[team_id][term_key] = row.value
        
        result = {}
        for team_id, term_values in teams_data.items():
            result[team_id] = TeamData.create(session_id, team_id, term_values)
            
        return result

class PostgreSQLApprovalRepository(IApprovalRepository):
    """The part that saves and loads the TBD/OK status for each term."""
    
    def __init__(self, unit_of_work: IUnitOfWork):
        self._unit_of_work = unit_of_work
    
    def save(self, approval: Approval) -> None:
        """Save approval state."""
        conn = self._unit_of_work.get_connection()
        
        check_stmt = select(approval_status).where(
            (approval_status.c.session_id == approval.session_id) &
            (approval_status.c.term_key == approval.term_key.value)
        )
        existing = conn.execute(check_stmt).fetchone()
        
        if existing:
            update_stmt = update(approval_status).where(
                (approval_status.c.session_id == approval.session_id) &
                (approval_status.c.term_key == approval.term_key.value)
            ).values(status=approval.status)
            conn.execute(update_stmt)
        else:
            insert_stmt = insert(approval_status).values(
                id=str(uuid4()),
                session_id=approval.session_id,
                term_key=approval.term_key.value,
                status=approval.status,
            )
            conn.execute(insert_stmt)
    
    def get_by_session(self, session_id: str) -> List[Approval]:
        """Get all approvals for a session."""
        conn = self._unit_of_work.get_connection()
        
        stmt = select(approval_status).where(
            approval_status.c.session_id == session_id
        )
        results = conn.execute(stmt).fetchall()
        
        return [
            Approval.create(
                session_id=result.session_id,
                term_key=TermKey(result.term_key),
                status=result.status
            ) for result in results
        ]
    
    def get_by_session_and_term(self, session_id: str, term_key: TermKey) -> Optional[Approval]:
        """Get approval state for specific term."""
        conn = self._unit_of_work.get_connection()
        
        stmt = select(approval_status).where(
            (approval_status.c.session_id == session_id) &
            (approval_status.c.term_key == term_key.value)
        )
        result = conn.execute(stmt).fetchone()
        
        if not result:
            return None
        
        return Approval.create(
            session_id=result.session_id,
            term_key=TermKey(result.term_key),
            status=result.status
        )
