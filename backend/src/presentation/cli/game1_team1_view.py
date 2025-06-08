from typing import Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.approval import ApprovalStatus
from ...infrastructure.containers import Container

class Game1Team1View:
    """Interface for Team 1 in Game 1."""
    
    def __init__(self, container: Container, console: Console):
        self.container = container
        self.console = console
        self.session_id: Optional[UUID] = None
        self.current_data: Dict[str, Any] = {}
        
    def set_session_id(self, session_id: UUID) -> None:
        """Set the current session ID."""
        self.session_id = session_id
        
    def render(self) -> Panel:
        """Display the Team 1 interface."""
        if not self.session_id:
            return Panel("Waiting for session...", title="Team 1 - Data Input")
        
        table = Table.grid()
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        
        input_panel = self._create_input_panel()
        
        status_panel = self._create_status_panel()
        
        table.add_row(input_panel, status_panel)
        
        return Panel(
            table,
            title="🏦 Team 1 - Financial Data Input",
            border_style="blue"
        )
    
    def _create_input_panel(self) -> Panel:
        """Create the input form panel."""
        input_table = Table(show_header=True, header_style="bold cyan")
        input_table.add_column("Field", style="cyan", width=15)
        input_table.add_column("Value", style="green", width=20)
        input_table.add_column("Status", style="yellow", width=10)
        
        session_status = self._get_session_status()
        if not session_status:
            team_data = {}
            approvals = {}
        else:
            team_data = session_status.team_data
            approvals = session_status.approvals
        
        ebitda_value = self._get_team_value(team_data, TermKey.EBITDA)
        ebitda_status = self._get_approval_status(approvals, TermKey.EBITDA)
        input_table.add_row(
            "EBITDA (₽)",
            f"{ebitda_value:,.0f}" if ebitda_value else "[dim]Not set[/dim]",
            ebitda_status
        )
        
        rate_value = self._get_team_value(team_data, TermKey.INTEREST_RATE)
        rate_status = self._get_approval_status(approvals, TermKey.INTEREST_RATE)
        input_table.add_row(
            "Interest Rate (%)",
            f"{rate_value:.1f}%" if rate_value else "[dim]Not set[/dim]",
            rate_status
        )
        
        multiple_value = self._get_team_value(team_data, TermKey.MULTIPLE)
        multiple_status = self._get_approval_status(approvals, TermKey.MULTIPLE)
        input_table.add_row(
            "Multiple",
            f"{multiple_value:.1f}x" if multiple_value else "[dim]Not set[/dim]",
            multiple_status
        )
        
        factor_value = self._get_team_value(team_data, TermKey.FACTOR_SCORE)
        factor_status = self._get_approval_status(approvals, TermKey.FACTOR_SCORE)
        input_table.add_row(
            "Factor Score",
            f"{factor_value:.1f}" if factor_value else "[dim]Not set[/dim]",
            factor_status
        )
        
        return Panel(input_table, title="📊 Your Data", border_style="cyan")
    
    def _create_status_panel(self) -> Panel:
        """Create the status and output panel."""
        session_status = self._get_session_status()
        if not session_status:
            valuation = None
            is_complete = False
        else:
            valuation = session_status.valuation
            is_complete = session_status.is_complete
        
        status_content = Text()
        
        if is_complete:
            status_content.append("🎉 Session Complete!\n", style="bold green")
            status_content.append(f"Final Valuation: {valuation:,.0f} ₽\n", style="bold blue")
        elif valuation:
            status_content.append("✅ All terms approved by Team 2\n", style="green")
            status_content.append(f"💰 Valuation: {valuation:,.0f} ₽\n", style="bold blue")
        else:
            status_content.append("⏳ Waiting for Team 2 approval\n", style="yellow")
            status_content.append("❌ Valuation: Not yet agreed\n", style="red")
        
        status_content.append("\n📋 Formula:\n", style="bold")
        status_content.append("Valuation = EBITDA × Multiple × Factor Score", style="dim")
        
        return Panel(
            Align.center(status_content),
            title="📈 Valuation Status",
            border_style="green" if valuation else "yellow"
        )
    
    def _get_session_status(self):
        """Get current session status as clean DTO."""
        if not self.session_id:
            return None
        
        try:
            game_service = self.container.game_service()
            return game_service.get_session_status(str(self.session_id))
        except Exception:
            return None
    
    def _get_team_value(self, team_data: Dict, term_key: TermKey) -> Optional[Decimal]:
        """Get value for specific term from team data DTOs."""
        team1_data = team_data.get(TeamId.TEAM_ONE)
        if not team1_data:
            return None
        return team1_data.term_values.get(term_key)
    
    def _get_approval_status(self, approvals: Dict, term_key: TermKey) -> str:
        """Get approval status for specific term from DTO."""
        if term_key in approvals:
            approval = approvals[term_key]
            if approval.status == ApprovalStatus.OK:
                return "[green]✅ OK[/green]"
            else:
                return "[yellow]⏳ TBD[/yellow]"
        return "[dim]➖ Pending[/dim]"
    
    def refresh_data(self) -> None:
        """Refresh data from backend."""
        self.current_data = self._get_session_status()
    
    def get_controls_help(self) -> Text:
        """Get help text for controls."""
        help_text = Text()
        help_text.append("🎮 Controls: ", style="bold")
        help_text.append("E", style="bold cyan")
        help_text.append("-EBITDA  ")
        help_text.append("R", style="bold cyan") 
        help_text.append("-Rate  ")
        help_text.append("M", style="bold cyan")
        help_text.append("-Multiple  ")
        help_text.append("F", style="bold cyan")
        help_text.append("-Factor  ")
        help_text.append("Ctrl+C", style="bold red")
        help_text.append("-Exit")
        return help_text
    
    def cleanup(self) -> None:
        """Cleanup resources when view is destroyed."""
        pass 