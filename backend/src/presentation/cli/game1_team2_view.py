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
from ...infrastructure.containers import Container

class Game1Team2View:
    """Interface for Team 2 in Game 1."""
    
    def __init__(self, container: Container, console: Console):
        self.container = container
        self.console = console
        self.session_id: Optional[UUID] = None
        self.current_data: Dict[str, Any] = {}
        
    def set_session_id(self, session_id: UUID) -> None:
        """Set the current session ID for data access."""
        self.session_id = session_id
        
    def render(self) -> Panel:
        """Draws the whole screen for Team 2, splitting it into two panels."""
        if not self.session_id:
            return Panel("Waiting for session...", title="Team 2 - Approval Control")
        
        table = Table.grid()
        table.add_column(ratio=1)
        table.add_column(ratio=1)
        
        approval_panel = self._create_approval_panel()
        output_panel = self._create_output_panel()
        
        table.add_row(approval_panel, output_panel)
        
        return Panel(
            table,
            title="⚖️ Team 2 - Term Approval & Negotiation",
            border_style="green"
        )
    
    def _create_approval_panel(self) -> Panel:
        """Builds the left-side table where you see Team 1's numbers and can approve them."""
        approval_table = Table(show_header=True, header_style="bold green")
        approval_table.add_column("Term", style="cyan", width=15)
        approval_table.add_column("Team 1 Value", style="blue", width=18)
        approval_table.add_column("Your Decision", style="yellow", width=12)
        approval_table.add_column("Action", style="magenta", width=8)
        
        session_status = self._get_session_status()
        if not session_status:
            approval_table.add_row("EBITDA (₽)", "[dim]Waiting for Team 1...[/dim]", "[dim]➖ Pending[/dim]", "[dim]-[/dim]")
            approval_table.add_row("Interest Rate (%)", "[dim]Waiting for Team 1...[/dim]", "[dim]➖ Pending[/dim]", "[dim]-[/dim]")
            approval_table.add_row("Multiple", "[dim]Waiting for Team 1...[/dim]", "[dim]➖ Pending[/dim]", "[dim]-[/dim]")
            approval_table.add_row("Factor Score", "[dim]Waiting for Team 1...[/dim]", "[dim]➖ Pending[/dim]", "[dim]-[/dim]")
            return Panel(approval_table, title="📋 Terms for Approval", border_style="cyan")
            
        team_data = session_status.team_data
        approvals = session_status.approvals
        
        ebitda_value = self._get_team_value(team_data, TermKey.EBITDA)
        ebitda_approval = approvals.get(TermKey.EBITDA) if approvals else None
        approval_table.add_row(
            "EBITDA (₽)",
            f"{ebitda_value:,.0f}" if ebitda_value else "[dim]Waiting...[/dim]",
            self._format_approval_status(ebitda_approval),
            "[bold cyan]1[/bold cyan]" if ebitda_value else "[dim]-[/dim]"
        )
        
        rate_value = self._get_team_value(team_data, TermKey.INTEREST_RATE)
        rate_approval = approvals.get(TermKey.INTEREST_RATE) if approvals else None
        approval_table.add_row(
            "Interest Rate (%)",
            f"{rate_value:.1f}%" if rate_value else "[dim]Waiting...[/dim]",
            self._format_approval_status(rate_approval),
            "[bold cyan]2[/bold cyan]" if rate_value else "[dim]-[/dim]"
        )
        
        multiple_value = self._get_team_value(team_data, TermKey.MULTIPLE)
        multiple_approval = approvals.get(TermKey.MULTIPLE) if approvals else None
        approval_table.add_row(
            "Multiple",
            f"{multiple_value:.1f}x" if multiple_value else "[dim]Waiting...[/dim]",
            self._format_approval_status(multiple_approval),
            "[bold cyan]3[/bold cyan]" if multiple_value else "[dim]-[/dim]"
        )
        
        factor_value = self._get_team_value(team_data, TermKey.FACTOR_SCORE)
        factor_approval = approvals.get(TermKey.FACTOR_SCORE) if approvals else None
        approval_table.add_row(
            "Factor Score",
            f"{factor_value:.1f}" if factor_value else "[dim]Waiting...[/dim]",
            self._format_approval_status(factor_approval),
            "[bold cyan]4[/bold cyan]" if factor_value else "[dim]-[/dim]"
        )
        
        return Panel(approval_table, title="📋 Terms for Approval", border_style="cyan")
    
    def _create_output_panel(self) -> Panel:
        """Builds the right-side panel that shows if the deal is done and what the final number is."""
        session_status = self._get_session_status()
        if not session_status:
            status_content = Text()
            status_content.append("⏳ Waiting for Team 1\n", style="yellow")
            status_content.append("No data available yet\n\n", style="dim")
            status_content.append("📋 Valuation Formula:\n", style="bold")
            status_content.append("EBITDA × Multiple × Factor Score", style="dim")
            return Panel(Align.center(status_content), title="📈 Negotiation Status", border_style="yellow")
            
        valuation = session_status.valuation
        is_complete = session_status.is_complete
        approvals = session_status.approvals
        
        status_content = Text()
        
        if is_complete:
            status_content.append("🎉 Deal Closed!\n", style="bold green")
            status_content.append(f"Final Valuation: {valuation:,.0f} ₽\n\n", style="bold blue")
        elif valuation:
            status_content.append("✅ All Terms Approved!\n", style="bold green")
            status_content.append(f"💰 Agreed Valuation: {valuation:,.0f} ₽\n\n", style="bold blue")
        else:
            status_content.append("⏳ Negotiation in Progress\n", style="yellow")
            status_content.append("❌ No valuation yet\n\n", style="red")
        
        status_content.append("📊 Approval Summary:\n", style="bold")
        
        approved_count = sum(1 for approval in approvals.values() if approval and approval.is_approved)
        total_terms = 4
        
        if approved_count == total_terms:
            status_content.append(f"✅ {approved_count}/{total_terms} terms approved\n", style="green")
        else:
            status_content.append(f"⏳ {approved_count}/{total_terms} terms approved\n", style="yellow")
        
        status_content.append("\n📋 Valuation Formula:\n", style="bold")
        status_content.append("EBITDA × Multiple × Factor Score", style="dim")
        
        return Panel(
            Align.center(status_content),
            title="📈 Negotiation Status",
            border_style="green" if valuation else "yellow"
        )
    
    def _format_approval_status(self, approval) -> str:
        """Makes the TBD/OK status look pretty with colors and icons."""
        if not approval:
            return "[dim]➖ Pending[/dim]"
        elif approval.is_approved:
            return "[bold green]✅ APPROVED[/bold green]"
        else:
            return "[bold yellow]⏳ REVIEWING[/bold yellow]"
    
    def _get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        if not self.session_id:
            return {}
        
        try:
            game_service = self.container.game_service()
            result = game_service.get_session_status(str(self.session_id))
            return result
        except Exception as e:
            return {}
    
    def _get_team_value(self, team_data: Dict, term_key: TermKey) -> Optional[Decimal]:
        """Digs into the big data object to find one specific number from Team 1."""
        team1_data = team_data.get(TeamId.TEAM_ONE)
        if not team1_data:
            return None
        
        if not self._is_team1_data_complete(team_data):
            return None
            
        return team1_data.term_values.get(term_key)
    
    def _is_team1_data_complete(self, team_data: Dict) -> bool:
        """Checks if Team 1 has actually entered all their numbers yet."""
        from ...domain.value_objects.term_key import TermKey
        from ...domain.services.game_configuration import GameConfiguration
        from ...domain.value_objects.game_type import GameType
        
        team1_data = team_data.get(TeamId.TEAM_ONE)
        if not team1_data:
            return False
        
        required_terms = GameConfiguration.get_game_terms(GameType.GAME_1)
        
        for term_key in required_terms:
            if term_key not in team1_data.term_values or team1_data.term_values[term_key] is None:
                return False
        
        return True
    
    def refresh_data(self) -> None:
        """Just re-fetches all the data from the backend."""
        self.current_data = self._get_session_status()
    
    def get_controls_help(self) -> Text:
        """Get help text for controls."""
        help_text = Text()
        help_text.append("🎮 Controls: ", style="bold")
        help_text.append("1", style="bold cyan")
        help_text.append("-EBITDA  ")
        help_text.append("2", style="bold cyan") 
        help_text.append("-Rate  ")
        help_text.append("3", style="bold cyan")
        help_text.append("-Multiple  ")
        help_text.append("4", style="bold cyan")
        help_text.append("-Factor  ")
        help_text.append("Ctrl+C", style="bold red")
        help_text.append("-Exit")
        return help_text
    
    def cleanup(self) -> None:
        """Does nothing for now, but might be needed later."""
        pass 