import redis
from typing import Optional
import gevent.lock
from redis.exceptions import ConnectionError, TimeoutError

class RedisConnection:
    """Handles our connection to Redis. It's a singleton so we don't open a million connections."""
    
    def __init__(self, redis_url: str):
        self._redis_url = redis_url
        self._redis_client: Optional[redis.Redis] = None
        self._connection_lock = gevent.lock.RLock()
    
    def get_client(self) -> redis.Redis:
        """Get Redis client, creating if necessary."""
        if self._redis_client is None:
            with self._connection_lock:
                if self._redis_client is None:
                    self._redis_client = redis.from_url(
                        self._redis_url,
                        socket_connect_timeout=5,
                        socket_timeout=5,
                        retry_on_timeout=True,
                        health_check_interval=30,
                        decode_responses=True,
                    )
        return self._redis_client
    
    def ping(self) -> bool:
        """Health check for Redis connection."""
        try:
            return self.get_client().ping()
        except (ConnectionError, TimeoutError):
            return False
    
    def close(self) -> None:
        """Close Redis connection."""
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None 