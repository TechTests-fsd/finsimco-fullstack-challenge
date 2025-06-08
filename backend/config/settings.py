from pydantic import BaseSettings

class Settings(BaseSettings):
    """All the app's settings. Pydantic magically loads these from a .env file or environment variables."""
    
    database_url: str
    redis_url: str
    log_level: str
    log_format: str
    log_date_format: str
    log_file: str
    log_max_bytes: int
    log_backup_count: int
    
    class Config:
        env_file = ".env"
        case_sensitive = False
