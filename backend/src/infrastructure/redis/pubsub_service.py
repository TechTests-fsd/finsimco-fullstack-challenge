import json
import logging
import time
import gevent
from typing import Dict, Any, Callable, Optional
from decimal import Decimal
from .connection import RedisConnection
from ...application.ports.pubsub import IPubSubService
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.approval import ApprovalStatus

logger = logging.getLogger(__name__)


class PubSubService(IPubSubService):
    """The thing that shouts messages between the two running programs using Redis."""
    
    def __init__(self, redis_connection: RedisConnection):
        self._redis = redis_connection
        self._subscribers: Dict[str, Callable] = {}
        self._pubsub = None
        self._listening = False
        
    def publish_team_data_update(
        self, 
        session_id: str, 
        team_id: TeamId, 
        term_key: TermKey, 
        value: Decimal
    ) -> None:
        """Publish team data update to all subscribers."""
        channel = f"session:{session_id}:team_data"
        message = {
            "type": "team_data_update",
            "team_id": team_id.value,
            "term_key": term_key.value,
            "value": str(value), 
            "timestamp": time.time()
        }
        
        logger.info(f"Publishing team data update: {channel} -> {message}")
        result = self._redis.get_client().publish(channel, json.dumps(message))
        logger.info(f"Published to {result} subscribers")
    
    def publish_approval_update(
        self, 
        session_id: str, 
        term_key: TermKey, 
        status: ApprovalStatus
    ) -> None:
        """Publish approval status update to all subscribers."""
        channel = f"session:{session_id}:approvals"
        message = {
            "type": "approval_update",
            "term_key": term_key.value,
            "status": status.value,
            "timestamp": time.time()
        }
        
        self._redis.get_client().publish(channel, json.dumps(message))
    
    def publish_session_completed(self, session_id: str) -> None:
        """Publish session completion notification."""
        channel = f"session:{session_id}:status"
        message = {
            "type": "session_completed",
            "timestamp": time.time()
        }
        
        self._redis.get_client().publish(channel, json.dumps(message))
    
    def subscribe_to_session(
        self, 
        session_id: str, 
        team_data_callback: Optional[Callable] = None,
        approval_callback: Optional[Callable] = None,
        session_callback: Optional[Callable] = None
    ) -> None:
        """Subscribe to session updates with callbacks."""
        channels = []
        
        if team_data_callback:
            channel = f"session:{session_id}:team_data"
            channels.append(channel)
            self._subscribers[channel] = team_data_callback
            
        if approval_callback:
            channel = f"session:{session_id}:approvals"
            channels.append(channel)
            self._subscribers[channel] = approval_callback
            
        if session_callback:
            channel = f"session:{session_id}:status"
            channels.append(channel)
            self._subscribers[channel] = session_callback
        
        if channels:
            logger.info(f"Subscribing to session {session_id} channels: {channels}")
            self._start_listening(channels)
        else:
            logger.warning(f"No callbacks provided for session {session_id}, skipping subscription")
    
    def _start_listening(self, channels: list) -> None:
        """Kicks off the background process that actually listens to Redis."""
        if not self._listening:
            self._pubsub = self._redis.get_client().pubsub()
            self._pubsub.subscribe(channels)
            self._listening = True
            
            gevent.spawn(self._listen_loop) 
    
    def _listen_loop(self) -> None:
        """Background loop for processing Redis messages."""
        try:
            logger.info("Starting PubSub listen loop")
            for message in self._pubsub.listen():
                if message['type'] == 'message':
                    channel = message['channel']
                    data = json.loads(message['data'])
                    
                    logger.info(f"Received message on {channel}: {data}")
                    
                    if channel in self._subscribers:
                        callback = self._subscribers[channel]
                        logger.info(f"Calling callback for channel {channel}")
                        gevent.spawn(callback, data)
                    else:
                        logger.warning(f"No callback registered for channel {channel}")
                        
        except Exception as e:
            logger.error(f"PubSub error: {e}")
        finally:
            self._listening = False
    
    def stop_listening(self) -> None:
        """Stop listening and cleanup resources."""
        if self._pubsub:
            self._pubsub.close()
            self._pubsub = None
        self._listening = False
        self._subscribers.clear() 