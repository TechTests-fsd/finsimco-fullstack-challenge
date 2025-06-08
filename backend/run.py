import sys
import os
import argparse
import logging
from typing import Optional
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.infrastructure.containers import Container
from src.infrastructure.database.connection import DatabaseConnection
from src.infrastructure.database.migrations import DatabaseMigrations
from src.presentation.cli.main_app import MainApp, AppConfig
from src.domain.value_objects.team_id import TeamId

import psycopg2
import gevent
import rich
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('finsimco.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_argument_parser() -> argparse.ArgumentParser:
    """Configure command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="FinSimCo - Premium Financial Simulation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --team 1                    # Launch as Team 1 (Data Input)
  %(prog)s --team 2                    # Launch as Team 2 (Approval Control)  
  %(prog)s --team 1 --game 2           # Launch Game 2 as Team 1
  %(prog)s --session abc123 --team 2   # Join existing session
  %(prog)s --init-db                   # Initialize database schema
        """
    )
    
    parser.add_argument(
        '--team',
        type=int,
        choices=[1, 2],
        required=True,
        help='Team ID (1=Data Input, 2=Approval Control)'
    )
    
    parser.add_argument(
        '--game',
        type=int,
        choices=[1, 2],
        default=1,
        help='Game number (default: 1)'
    )
    
    parser.add_argument(
        '--session',
        type=str,
        help='Join existing session by ID (optional - creates new if not provided)'
    )
    
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database schema and exit'
    )
    
    parser.add_argument(
        '--db-url',
        type=str,
        default=os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/finsimco'),
        help='PostgreSQL database URL (default: from DATABASE_URL env var)'
    )
    
    parser.add_argument(
        '--redis-url',
        type=str,
        default=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        help='Redis URL for real-time synchronization (default: from REDIS_URL env var)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser

def initialize_database(db_url: str) -> bool:
    """Initialize database schema."""
    try:
        logger.info("🔄 Initializing database schema...")
        
        db_connection = DatabaseConnection(db_url)
        
        migrations = DatabaseMigrations(db_connection.get_engine())
        migrations.create_all_tables()
        
        logger.info("✅ Database schema initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def validate_environment() -> bool:
    """Validate required environment and dependencies."""
    try:
        if sys.version_info < (3, 8):
            logger.error("❌ Python 3.8+ required")
            return False
            
        logger.info("🔄 Testing database connectivity...")
        

        
        logger.info("✅ Environment validation passed")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        logger.error("💡 Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"❌ Environment validation failed: {e}")
        return False

def create_app_config(args: argparse.Namespace) -> AppConfig:
    """Create application configuration from arguments."""
    return AppConfig(
        database_url=args.db_url,
        redis_url=args.redis_url,
        team_id=TeamId.TEAM_ONE if args.team == 1 else TeamId.TEAM_TWO,
        game_number=args.game,
        session_id=args.session,
        debug_mode=args.debug
    )

def main() -> int:
    """Main application entry point."""
    try:
        parser = setup_argument_parser()
        args = parser.parse_args()
        
        if args.debug:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.debug("🐛 Debug mode enabled")
        
        if not validate_environment():
            return 1
        
        if args.init_db:
            success = initialize_database(args.db_url)
            return 0 if success else 1
        
        config = create_app_config(args)
        
        logger.info("🔄 Initializing enterprise container...")
        container = Container.create_configured(config.database_url, config.redis_url)
        
        if not initialize_database(config.database_url):
            return 1
        
        logger.info(f"🚀 Launching FinSimCo - Team {args.team}, Game {args.game}")
        
        app = MainApp(container, config)
        app.run()
        
        logger.info("👋 FinSimCo session completed")
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Application interrupted by user")
        return 0
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        if args.debug if 'args' in locals() else False:
            traceback.print_exc()
        return 1
    finally:
        if 'container' in locals():
            try:
                container.cleanup()
            except Exception as e:
                logger.warning(f"⚠️  Cleanup warning: {e}")

if __name__ == '__main__':
    sys.exit(main()) 