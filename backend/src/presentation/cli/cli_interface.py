from typing import Optional, Dict, Any, Type
from uuid import UUID
from decimal import Decimal, InvalidOperation
import gevent
from gevent.event import Event
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, FloatPrompt
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.approval import ApprovalStatus
from ...application.handlers.update_team_data_handler import UpdateTeamDataHandler
from ...application.handlers.toggle_approval_handler import ToggleApprovalHandler
from ...infrastructure.containers import Container
from ...domain.services.game_configuration import GameConfiguration
from ...domain.services.term_validation_service import TermValidationService
from ...domain.value_objects.validation_error import ValidationSeverity

class CLIInterface:
    """Handles user input and interaction for the CLI views."""   

    def __init__(self, container, console: Console):
        self.container = container
        self.console = console
        self.session_id: Optional[UUID] = None
        self.team_id: Optional[TeamId] = None
        self.current_values: Dict[TermKey, Decimal] = {}
        self._should_exit = Event()
        
    def set_context(self, session_id: UUID, team_id: TeamId):
        """Set session and team context."""
        self.session_id = session_id
        self.team_id = team_id
    
    def handle_team1_input(self, term_key: TermKey) -> None:
        """Guides Team 1 through inputting and validating a single term value."""
        if not self.session_id or not self.team_id:
            self.console.print("❌ [red]Session not initialized[/red]")
            return
            
        try:
            term_metadata = GameConfiguration.get_term_metadata(term_key)
        except KeyError:
            self.console.print(f"❌ [red]Unknown term: {term_key.value}[/red]")
            return
            
        self._display_input_context(term_key, term_metadata)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                value = self._get_validated_input(term_key, term_metadata, attempt)
                if value is not None:
                    self._submit_team_data(term_key, value)
                    break
            except KeyboardInterrupt:
                self.console.print("\n⏸️  [yellow]Input cancelled[/yellow]")
                break
            except Exception as e:
                self.console.print(f"❌ [red]Unexpected error: {e}[/red]")
                if attempt == max_attempts - 1:
                    self.console.print("❌ [red]Maximum attempts reached[/red]")
    
    def handle_team2_approval(self, term_key: TermKey) -> None:
        """Toggles the approval status for a given term on behalf of Team 2."""
        if not self.session_id:
            self.console.print("❌ [red]Session not initialized[/red]")
            return
        
        try:
            game_service = self.container.game_service()
            current_status = game_service.get_approval_status(str(self.session_id), term_key)
            
            if current_status is None:
                new_status = ApprovalStatus.OK  
            else:
                new_status = ApprovalStatus.OK if current_status == ApprovalStatus.TBD else ApprovalStatus.TBD
            
            actual_new_status = game_service.toggle_approval_status(str(self.session_id), term_key)
            
            status_text = "✅ APPROVED" if actual_new_status == ApprovalStatus.OK else "⏳ PENDING"
            status_color = "green" if actual_new_status == ApprovalStatus.OK else "yellow"
            
            term_metadata = GameConfiguration.get_term_metadata(term_key)
            field_name = term_metadata.display_name
            self.console.print(f"🔄 [bold]{field_name}[/bold]: [{status_color}]{status_text}[/{status_color}]")
            
        except Exception as e:
            self.console.print(f"❌ [red]Failed to toggle approval: {e}[/red]")
    
    def _display_input_context(self, term_key: TermKey, term_metadata) -> None:
        """Display context information for input."""
        name = term_metadata.display_name
        unit = term_metadata.unit
        min_val = term_metadata.min_value
        max_val = term_metadata.max_value
        
        context_table = Table(show_header=False, box=None, padding=(0, 1))
        context_table.add_column("Field", style="bold cyan")
        context_table.add_column("Value")
        
        context_table.add_row("Field:", f"{name}")
        context_table.add_row("Range:", f"{min_val} - {max_val} {unit}")
        context_table.add_row("Precision:", f"{term_metadata.precision} decimal places")
        
        if term_metadata.business_rules:
            for rule in term_metadata.business_rules:
                rule_display = rule.name.replace("_", " ").title()
                context_table.add_row(f"{rule_display}:", f"{rule.min_value} - {rule.max_value} {unit}")
        
        panel = Panel(
            context_table,
            title=f"💼 Enter {name}",
            title_align="left",
            border_style="blue"
        )
        self.console.print(panel)
    
    def _get_validated_input(self, term_key: TermKey, term_metadata, attempt: int) -> Optional[float]:
        """Prompts the user for a value, validates it, and handles confirmation."""
        name = term_metadata.display_name
        unit = term_metadata.unit
        
        prompt_text = f"Enter {name}"
        if unit:
            prompt_text += f" ({unit})"
        if attempt > 0:
            prompt_text += f" [attempt {attempt + 1}/3]"
        prompt_text += ": "
        
        try:
            input_str = Prompt.ask(prompt_text).strip()
            
            if not input_str:
                self.console.print("⚠️  [yellow]Empty input - please enter a value[/yellow]")
                return None
                
            value_decimal = Decimal(input_str)
            
            errors = TermValidationService.validate_term_value(term_key, value_decimal)
            
            if not errors:
                self.console.print(f"✅ [green]Input valid for {term_metadata.display_name}[/green]")
                return float(value_decimal)
            
            critical_errors = [e for e in errors if e.severity == ValidationSeverity.ERROR]
            warnings = [e for e in errors if e.severity == ValidationSeverity.WARNING]
            infos = [e for e in errors if e.severity == ValidationSeverity.INFO]
            
            self._render_validation_results(critical_errors, warnings, infos)
            
            if critical_errors:
                return None  
            
            if warnings:
                confirm = Prompt.ask("⚠️  [yellow]Continue with warnings? (y/N)[/yellow]").lower()
                if confirm != 'y':
                    return None
            
            return float(value_decimal)
                
        except ValueError:
            self.console.print("❌ [red]Invalid number format. Please enter a valid number.[/red]")
            return None
        except InvalidOperation:
            self.console.print("❌ [red]Number too large or invalid format.[/red]")
            return None
    
    def _render_validation_results(self, critical_errors, warnings, infos) -> None:
        """Displays a formatted table of validation errors and warnings."""
        if not (critical_errors or warnings or infos):
            return
            
        validation_table = Table(show_header=True, box=None)
        validation_table.add_column("Severity", style="bold")
        validation_table.add_column("Code", style="dim")
        validation_table.add_column("Message")
        
        for error in critical_errors:
            validation_table.add_row(
                "❌ Error", 
                error.code, 
                error.message,
                style="red"
            )
        
        for error in warnings:
            validation_table.add_row(
                "⚠️  Warning", 
                error.code, 
                error.message,
                style="yellow"
            )
        
        for error in infos:
            validation_table.add_row(
                "ℹ️  Info", 
                error.code, 
                error.message,
                style="blue"
            )
        
        border_style = "red" if critical_errors else "yellow" if warnings else "blue"
        panel = Panel(
            validation_table,
            title="🔍 Validation Results",
            title_align="left",
            border_style=border_style
        )
        self.console.print(panel)
    
    def _submit_team_data(self, term_key: TermKey, value: float) -> None:
        """Submit validated data to game service."""
        try:
            game_service = self.container.game_service()
            game_service.update_team_data(str(self.session_id), self.team_id, term_key, Decimal(str(value)))
            
            self.console.print("🚀 [green]Data submitted successfully![/green]")
            
        except Exception as e:
            self.console.print(f"❌ [red]Failed to submit data: {e}[/red]")
    
    def display_session_status(self, session_id: UUID) -> None:
        """Display current session status with formatting."""
        try:
            game_service = self.container.game_service()
            status = game_service.get_session_status(session_id)
            
            if not status:
                self.console.print("❌ [red]Session not found[/red]")
                return
            
            status_panel = Panel(
                f"Session: {session_id}\nStatus: {status.game_session.status if status else 'Unknown'}",
                title="📊 Session Status",
                border_style="cyan"
            )
            self.console.print(status_panel)
            
        except Exception as e:
            self.console.print(f"❌ [red]Failed to get session status: {e}[/red]")
        
    def should_exit(self) -> bool:
        """Check if interface should exit."""
        return self._should_exit.is_set()
        
    def show_help_panel(self, team_id: TeamId) -> Panel:
        """Generate help panel with controls specific to the team's role."""
        if team_id == TeamId.TEAM_ONE:
            help_text = Text()
            help_text.append("🎮 Team 1 Controls:\n\n", style="bold blue")
            help_text.append("E", style="bold cyan")
            help_text.append(" - Edit EBITDA\n")
            help_text.append("R", style="bold cyan")
            help_text.append(" - Edit Interest Rate\n")
            help_text.append("M", style="bold cyan")
            help_text.append(" - Edit Multiple\n")
            help_text.append("F", style="bold cyan")
            help_text.append(" - Edit Factor Score\n\n")
            help_text.append("Ctrl+C", style="bold red")
            help_text.append(" - Exit simulation")
            
            return Panel(
                Align.center(help_text),
                title="📋 Help - Data Input",
                border_style="blue"
            )
        else:
            help_text = Text()
            help_text.append("🎮 Team 2 Controls:\n\n", style="bold green")
            help_text.append("1", style="bold cyan")
            help_text.append(" - Toggle EBITDA approval\n")
            help_text.append("2", style="bold cyan")
            help_text.append(" - Toggle Interest Rate approval\n")
            help_text.append("3", style="bold cyan")
            help_text.append(" - Toggle Multiple approval\n")
            help_text.append("4", style="bold cyan")
            help_text.append(" - Toggle Factor Score approval\n\n")
            help_text.append("Ctrl+C", style="bold red")
            help_text.append(" - Exit simulation")
            
            return Panel(
                Align.center(help_text),
                title="📋 Help - Approval Control",
                border_style="green"
            ) 