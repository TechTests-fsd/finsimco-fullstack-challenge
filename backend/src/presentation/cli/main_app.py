import gevent
from typing import Dict, Any, Optional
from uuid import UUID
from dataclasses import dataclass
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import print as rprint
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.game_type import GameType
from ...domain.services.game_configuration import GameConfiguration
from ...infrastructure.containers import Container
from ...infrastructure.database.migrations import DatabaseMigrations
from .game1_team1_view import Game1Team1View
from .game1_team2_view import Game1Team2View
from .game2_team1_view import Game2Team1View
from .game2_team2_view import Game2Team2View
from .cli_interface import CLIInterface

# Timing constants for gevent operations
MAIN_LOOP_SLEEP_SECONDS = 0.1
SYNC_INTERVAL_SECONDS = 1.0
ERROR_BACKOFF_SECONDS = 5.0

@dataclass
class AppConfig:
    """Application configuration."""
    database_url: str
    redis_url: str
    team_id: TeamId
    game_number: int
    session_id: Optional[str] = None
    debug_mode: bool = False

class MainApp:
    """The main class that runs the whole show. Kicks everything off."""
    
    def __init__(self, container: Container, config: AppConfig):
        self.container = container
        self.config = config
        self.console = Console()
        self.session_id: Optional[UUID] = None
        self.running = True
        
        self.team_id = config.team_id
        self.game_type = GameType(config.game_number)
        
        self._setup_database()
        
        self.view = self._create_view()
        self.cli_interface = CLIInterface(container, self.console)
        
        self._setup_keyboard_handlers()
    
    def run(self) -> None:
        """Run the main application loop."""
        try:
            self._show_welcome()
            self._create_or_join_session()
            
            if self.game_type == GameType.GAME_2:
                self._run_game2_interface()
            else:
                self._run_game1_interface()
                
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
        finally:
            self._cleanup()
    
    def _run_game1_interface(self) -> None:
        """The main loop for Game 1."""
        self.console.print("\n[bold green]Game 1 Interface Active[/bold green]")
        self.console.print(self.view.get_controls_help())
        
        import time
        last_refresh = time.time()
        last_data_hash = None
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - last_refresh > 2.0:
                    self.view.refresh_data()
                    last_refresh = current_time
                
                if self._check_game1_completion():
                    self._show_game1_completion()
                    break
                
                current_data = getattr(self.view, 'current_data', None)
                if current_data:
                    data_hash = str({
                        'team_data': {str(k): {
                            'term_values': dict(v.term_values) if hasattr(v, 'term_values') else {}
                        } for k, v in current_data.team_data.items()} if hasattr(current_data, 'team_data') else {},
                        'approvals': {str(k): str(v.status) for k, v in current_data.approvals.items()} if hasattr(current_data, 'approvals') else {},
                        'valuation': current_data.valuation if hasattr(current_data, 'valuation') else None,
                        'is_complete': current_data.is_complete if hasattr(current_data, 'is_complete') else False
                    })
                else:
                    data_hash = "None"
                    
                if data_hash != last_data_hash:
                    last_data_hash = data_hash
                    
                    self.console.clear()
                    self.console.print(self._create_header())
                    self.console.print(self.view.render())
                    self.console.print(self._create_footer())
                
                self._handle_interactive_input()
                
            except KeyboardInterrupt:
                self.running = False
                break
    
    def _run_game2_interface(self) -> None:
        """The main loop for Game 2."""
        self.console.print("\n[bold green]Game 2 Interface Active[/bold green]")
        self.console.print(self.view.get_controls_help())
        
        import time
        last_refresh = time.time()
        last_data_hash = None
        force_redraw = True  
        
        while self.running:
            try:
                current_time = time.time()
                if current_time - last_refresh > 2.0:
                    self.view.refresh_data()
                    last_refresh = current_time
                
                if self._check_game2_completion():
                    self._show_game2_completion()
                    break
                
                current_data = getattr(self.view, 'current_data', None)
                if current_data:
                    data_hash = str({
                        'team_data': {str(k): {
                            'term_values': dict(v.term_values) if hasattr(v, 'term_values') else {}
                        } for k, v in current_data.team_data.items()} if hasattr(current_data, 'team_data') else {},
                        'approvals': {str(k): str(v.status) for k, v in current_data.approvals.items()} if hasattr(current_data, 'approvals') else {},
                        'is_complete': current_data.is_complete if hasattr(current_data, 'is_complete') else False
                    })
                else:
                    data_hash = "None"
                    
                if data_hash != last_data_hash or force_redraw:
                    last_data_hash = data_hash
                    force_redraw = False
                    
                    self.console.clear()
                    self.console.print(self._create_header())
                    self.console.print(self.view.render())
                    self.console.print(self._create_footer_game2())
                
                command_executed = self._handle_interactive_input_game2()
                if command_executed:
                    force_redraw = True
                
            except KeyboardInterrupt:
                self.running = False
                break
    
    def _check_game2_completion(self) -> bool:
        """Check if Game 2 is complete via deal approvals."""
        try:
            game_service = self.container.game_service()
            status_dto = game_service.get_session_status(str(self.session_id))
            return status_dto.is_complete if status_dto else False
        except Exception:
            return False
    
    def _show_game2_completion(self) -> None:
        """Show Game 2 completion message with final summary."""
        self.console.clear()
        
        try:
            game_service = self.container.game_service()
            summary_data = game_service.calculate_game2_summary(str(self.session_id))
            
            completion_message = GameConfiguration.get_completion_message(self.game_type)
            
            final_summary = f"""
[bold green]{completion_message}[/bold green]

[bold cyan]Final Results:[/bold cyan]

[bold yellow]Company Performance:[/bold yellow]
"""
            
            if summary_data.get('companies'):
                companies = summary_data['companies']
                for i in range(1, 4):
                    company_data = companies.get(f'company{i}', {})
                    shares_bid = company_data.get('shares_bid_for', 0)
                    capital_raised = company_data.get('capital_raised', 'N/A')
                    subscription = company_data.get('subscription', 'N/A')
                    
                    final_summary += f"""
Company {i}:
  • Shares Bid For: {shares_bid}
  • Capital Raised: {capital_raised}
  • Subscription: {subscription}"""
                
                most_bids = summary_data.get('most_bids_company', 'No data')
                final_summary += f"\n\n[bold yellow]Winner:[/bold yellow] {most_bids} received the most investor interest!"
            
            final_summary += f"\n\n[bold blue]Session ID: {self.session_id}[/bold blue]"
            final_summary += "\n[dim]Press Ctrl+C to exit[/dim]"
            
            self.console.print(Panel(final_summary, title="🎉 Game Complete!", style="green"))
            
        except Exception as e:
            completion_message = GameConfiguration.get_completion_message(self.game_type)
            self.console.print(Panel(
                f"[bold green]{completion_message}[/bold green]\n\n"
                f"[bold blue]Session ID: {self.session_id}[/bold blue]\n"
                f"[red]Error loading final summary: {e}[/red]\n\n"
                "[dim]Press Ctrl+C to exit[/dim]",
                title="🎉 Game Complete!",
                style="green"
            ))
        
        self.running = False
    
    def _setup_database(self) -> None:
        """Setup database tables."""
        db_connection = self.container.database_connection()
        migrations = DatabaseMigrations(db_connection.get_engine())
        migrations.create_all_tables()
    
    def _create_view(self):
        """The main loop for Game 2. Uses a command-based input style."""
        if self.game_type == GameType.GAME_1:
            if self.team_id == TeamId.TEAM_ONE:
                return Game1Team1View(self.container, self.console)
            else:
                return Game1Team2View(self.container, self.console)
        elif self.game_type == GameType.GAME_2:
            if self.team_id == TeamId.TEAM_ONE:
                return Game2Team1View(self.container, self.console)
            else:
                return Game2Team2View(self.container, self.console)
        else:
            raise ValueError(f"Unknown game type: {self.game_type}")
    
    def _show_welcome(self) -> None:
        """Show welcome screen."""
        game_name = "FBITDA Valuation" if self.game_type == GameType.GAME_1 else "Acquisition Deal"
        team_role = self._get_team_role_description()
        
        welcome_panel = Panel.fit(
            f"[bold blue]Financial Simulation - {game_name}[/bold blue]\n"
            f"[yellow]{team_role}[/yellow]\n\n"
            f"[green]Press Ctrl+C to exit[/green]",
            title="🏢 FinSimCo Simulation Platform",
            border_style="blue"
        )
        self.console.print(welcome_panel)
    
    def _get_team_role_description(self) -> str:
        """Get descriptive team role based on game and team."""
        return GameConfiguration.get_team_role_description(self.game_type, self.team_id)
    
    def _create_or_join_session(self) -> None:
        """Create new session or join existing one."""
        game_service = self.container.game_service()
        
        if self.config.session_id:
            try:
                from uuid import UUID
                session_uuid = UUID(self.config.session_id)
                
                status_dto = game_service.get_session_status(str(session_uuid))
                if status_dto:
                    self.session_id = session_uuid
                    self.console.print(f"[green]Joined session: {self.session_id}[/green]")
                else:
                    raise ValueError("Session not found")
                    
            except Exception as e:
                self.console.print(f"[red]Failed to join session: {e}[/red]")
                self.console.print("[yellow]Creating new session...[/yellow]")
                self._create_new_session(game_service)
        else:
            self._create_new_session(game_service)
        
        if hasattr(self.view, 'set_session_id'):
            self.view.set_session_id(self.session_id)
        elif hasattr(self.view, 'set_session'):
            self.view.set_session(self.session_id)
        
        self.cli_interface.set_context(self.session_id, self.team_id)
        
    def _create_new_session(self, game_service) -> None:
        """Create a new game session."""
        from uuid import uuid4
        session_id = str(uuid4())
        session_dto = game_service.create_game_session(session_id, self.game_type)
        self.session_id = session_dto.id  
        self.console.print(f"[green]Session created: {self.session_id}[/green]")
    
    def _create_layout(self) -> Layout:
        """Create the main layout for the application (Game 1 only)."""
        layout = Layout()
        layout.split_column(
            Layout(self._create_header(), size=3),
            Layout(self.view.render(), name="main"),
            Layout(self._create_footer(), size=3),
        )
        return layout
    
    def _create_header(self) -> Panel:
        """Create header panel."""
        header_text = Text()
        header_text.append("🏢 FinSimCo Simulation Platform", style="bold blue")
        header_text.append(f" | Game {self.game_type.value}", style="yellow")
        header_text.append(f" | Team {self.team_id.value}", style="green")
        
        return Panel(header_text, height=3)
    
    def _create_footer(self) -> Panel:
        """Create footer panel with controls."""
        footer_text = self.view.get_controls_help()
        return Panel(footer_text, title="Controls", height=3)
    
    def _setup_keyboard_handlers(self) -> None:
        """Setup keyboard event handlers (Game 1 only)."""
        self.key_handlers = {}
        
        if self.game_type == GameType.GAME_1:
            if self.team_id == TeamId.TEAM_ONE:
                self.key_handlers.update({
                    'e': lambda: self.cli_interface.handle_team1_input(TermKey.EBITDA),
                    'r': lambda: self.cli_interface.handle_team1_input(TermKey.INTEREST_RATE),
                    'm': lambda: self.cli_interface.handle_team1_input(TermKey.MULTIPLE),
                    'f': lambda: self.cli_interface.handle_team1_input(TermKey.FACTOR_SCORE),
                })
            else:
                self.key_handlers.update({
                    '1': lambda: self.cli_interface.handle_team2_approval(TermKey.EBITDA),
                    '2': lambda: self.cli_interface.handle_team2_approval(TermKey.INTEREST_RATE),
                    '3': lambda: self.cli_interface.handle_team2_approval(TermKey.MULTIPLE),
                    '4': lambda: self.cli_interface.handle_team2_approval(TermKey.FACTOR_SCORE),
                })

    def _handle_interactive_input(self) -> None:
        """Handle user input interactively with timeout for polling."""
        import sys
        import select
        
        try:
            ready, _, _ = select.select([sys.stdin], [], [], 0.5)
            if ready:
                self.console.print("\n[bold cyan]Enter command[/bold cyan]: ", end="")
                sys.stdout.flush()
                user_input = sys.stdin.readline()
                key = user_input.strip().lower()
                
                if key in ['q', 'quit', 'exit']:
                    self.running = False
                    return
                    
                handler = self.key_handlers.get(key)
                if handler:
                    handler()
                else:
                    self.console.print(f"[yellow]Unknown command: {key}[/yellow]")
                    self.console.print("Available commands: " + ", ".join(self.key_handlers.keys()))
                
        except (EOFError, KeyboardInterrupt):
            self.running = False
    
    def _sync_loop(self) -> None:
        """Background sync loop for real-time updates."""
        while self.running:
            try:
                gevent.sleep(SYNC_INTERVAL_SECONDS)
            except Exception as e:
                self.console.print(f"[red]Sync error: {e}[/red]")
                gevent.sleep(ERROR_BACKOFF_SECONDS)
    
    def _create_footer_game2(self) -> Panel:
        """Create footer panel for Game 2."""
        footer_text = self.view.get_controls_help()
        return Panel(footer_text, title="Controls", height=5)
    
    def _handle_interactive_input_game2(self) -> bool:
        """Handle user input for Game 2."""
        import sys
        import select
        
        try:
            ready, _, _ = select.select([sys.stdin], [], [], 0.5)
            if ready:
                self.console.print("\n[bold cyan]Enter command[/bold cyan]: ", end="")
                sys.stdout.flush()
                user_input = sys.stdin.readline()
                command = user_input.strip().lower()
                
                if command in ['q', 'quit', 'exit']:
                    self.running = False
                    return True
                    
                if hasattr(self.view, 'handle_command'):
                    self.view.handle_command(command)
                else:
                    self.console.print(f"[yellow]Unknown command: {command}[/yellow]")
                
                return True  
                
            return False  
              
        except (EOFError, KeyboardInterrupt):
            self.running = False
            return True

    def _cleanup(self) -> None:
        """Just tells the main loop to stop."""
        self.running = False

    def _check_game1_completion(self) -> bool:
        """Check if Game 1 is complete via all term approvals."""
        try:
            game_service = self.container.game_service()
            status_dto = game_service.get_session_status(str(self.session_id))
            return status_dto.is_complete if status_dto else False
        except Exception:
            return False

    def _show_game1_completion(self) -> None:
        """Show Game 1 completion message with final valuation."""
        self.console.clear()
        
        try:
            game_service = self.container.game_service()
            status_dto = game_service.get_session_status(str(self.session_id))
            
            completion_message = GameConfiguration.get_completion_message(self.game_type)
            
            final_summary = f"[bold green]{completion_message}[/bold green]\n\n"
            
            if status_dto and status_dto.valuation:
                final_summary += f"[bold cyan]Final Valuation Results:[/bold cyan]\n"
                final_summary += f"💰 Agreed Valuation: [bold blue]{status_dto.valuation:,.0f} ₽[/bold blue]\n\n"
                
                final_summary += f"[bold yellow]Approved Terms:[/bold yellow]\n"
                if status_dto.team_data.get(TeamId.TEAM_ONE):
                    team_data = status_dto.team_data[TeamId.TEAM_ONE]
                    term_values = team_data.term_values
                    
                    final_summary += f"• EBITDA: {term_values.get(TermKey.EBITDA, 'N/A'):,} ₽\n"
                    final_summary += f"• Interest Rate: {term_values.get(TermKey.INTEREST_RATE, 'N/A')}%\n"
                    final_summary += f"• Multiple: {term_values.get(TermKey.MULTIPLE, 'N/A')}x\n"
                    final_summary += f"• Factor Score: {term_values.get(TermKey.FACTOR_SCORE, 'N/A')}\n\n"
                
                final_summary += f"[bold green]✅ All terms approved by Team 2![/bold green]\n"
            else:
                final_summary += f"[yellow]⚠️ No valuation data available[/yellow]\n"
            
            final_summary += f"\n[bold blue]Session ID: {self.session_id}[/bold blue]\n"
            final_summary += "[dim]Press Ctrl+C to exit[/dim]"
            
            self.console.print(Panel(final_summary, title="🎉 Game Complete!", style="green"))
            
        except Exception as e:
            completion_message = GameConfiguration.get_completion_message(self.game_type)
            self.console.print(Panel(
                f"[bold green]{completion_message}[/bold green]\n\n"
                f"[bold blue]Session ID: {self.session_id}[/bold blue]\n"
                f"[red]Error loading final summary: {e}[/red]\n\n"
                "[dim]Press Ctrl+C to exit[/dim]",
                title="🎉 Game Complete!",
                style="green"
            ))
        
        self.running = False
