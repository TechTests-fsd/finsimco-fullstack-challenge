from sqlalchemy import (
    MetaData, Table, Column, String, Integer, Boolean, DateTime, 
    ForeignKey, DECIMAL, Enum as SQLEnum
)
from sqlalchemy.sql import func
from ...domain.value_objects.game_type import GameType
from ...domain.entities.game_session import SessionStatus
from ...domain.value_objects.approval import ApprovalStatus

metadata = MetaData()

game_sessions = Table(
    'game_sessions',
    metadata,
    Column('id', String(255), primary_key=True),
    Column('game_type', SQLEnum(GameType), nullable=False),
    Column('status', SQLEnum(SessionStatus), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('completed_at', DateTime(timezone=True), nullable=True),
)

team_data = Table(
    'team_data',
    metadata,
    Column('id', String(255), primary_key=True),
    Column('session_id', String(255), ForeignKey('game_sessions.id'), nullable=False),
    Column('team_id', Integer, nullable=False),
    Column('term_key', String(50), nullable=False),
    Column('value', DECIMAL(20, 2), nullable=False),
    Column('updated_at', DateTime(timezone=True), server_default=func.now()),
)

approval_status = Table(
    'approval_status',
    metadata,
    Column('id', String(255), primary_key=True),
    Column('session_id', String(255), ForeignKey('game_sessions.id'), nullable=False),
    Column('term_key', String(50), nullable=False),
    Column('status', SQLEnum(ApprovalStatus), nullable=False),
    Column('updated_at', DateTime(timezone=True), server_default=func.now()),
)

from sqlalchemy import Index

Index('idx_team_data_unique', team_data.c.session_id, team_data.c.team_id, team_data.c.term_key, unique=True)

Index('idx_approval_unique', approval_status.c.session_id, approval_status.c.term_key, unique=True) 