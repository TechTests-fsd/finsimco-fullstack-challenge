from uuid import UUID
from decimal import Decimal
from typing import Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.game_type import GameType
from ...domain.services.game_configuration import GameConfiguration
from ...domain.services.term_validation_service import TermValidationService
from ...application.dto.session_status_dto import SessionStatusDTO
from .cli_interface import CLIInterface

class Game2Team1View:
    """The screen for Team 1 in Game 2. Their job is to set prices for the companies."""
    
    def __init__(self, container, console: Console):
        self.container = container
        self.console = console
        self.cli = CLIInterface(container, console)
        self.session_id: UUID = None
        self.team_id = TeamId.TEAM_ONE
        self.current_data: Optional[SessionStatusDTO] = None
        self.validation_service = TermValidationService()
        
    def set_session_id(self, session_id: UUID):
        """Set the game session context."""
        self.session_id = session_id
        self.cli.set_context(session_id, self.team_id)
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Pulls the latest game state from the backend."""
        self.current_data = self._get_session_status()
    
    def render(self) -> Panel:
        """Draws the main table with company prices and shares."""
        table = Table(show_header=True, header_style="bold blue", width=80)
        table.add_column("Pricing", style="cyan", width=15)
        table.add_column("Company 1", style="green", width=15)
        table.add_column("Company 2", style="green", width=15) 
        table.add_column("Company 3", style="green", width=15)
        table.add_column("Unit", style="dim", width=10)
        
        pricing_data = self._get_team_pricing_data()
        
        table.add_row(
            "Price:",
            pricing_data.get('company1_price', "[dim]Not set[/dim]"),
            pricing_data.get('company2_price', "[dim]Not set[/dim]"),
            pricing_data.get('company3_price', "[dim]Not set[/dim]"),
            "#"
        )
        
        table.add_row(
            "Shares:",
            pricing_data.get('company1_shares', "[dim]Not set[/dim]"),
            pricing_data.get('company2_shares', "[dim]Not set[/dim]"),
            pricing_data.get('company3_shares', "[dim]Not set[/dim]"),
            "#"
        )
        
        return Panel(
            table,
            title="🏢 Team 1 - Company Pricing",
            subtitle="Set pricing for Company 1, 2, and 3",
            style="blue"
        )
    
    def _get_team_pricing_data(self) -> Dict[str, str]:
        """Pulls price/shares data out of the big session object for easy display."""
        if not self.current_data:
            return {f'company{i}_{field}': "[dim]Not set[/dim]" for i in range(1, 4) for field in ['price', 'shares']}
        
        team_data = self._get_team_data()
        if not team_data:
            return {f'company{i}_{field}': "[dim]Not set[/dim]" for i in range(1, 4) for field in ['price', 'shares']}
        
        result = {}
        for company_num in range(1, 4):
            company_terms = GameConfiguration.get_company_terms(company_num)
            price_key = company_terms['price']
            shares_key = company_terms['shares']
            
            result[f'company{company_num}_price'] = str(team_data.term_values.get(price_key, "[dim]Not set[/dim]"))
            result[f'company{company_num}_shares'] = str(team_data.term_values.get(shares_key, "[dim]Not set[/dim]"))
        
        return result
    
    def _get_team_data(self):
        """Get team data safely."""
        if not self.current_data or not hasattr(self.current_data, 'team_data'):
            return None
        return self.current_data.team_data.get(TeamId.TEAM_ONE)
    
    def _get_session_status(self) -> Optional[SessionStatusDTO]:
        """Get current session status."""
        try:
            game_service = self.container.game_service()
            return game_service.get_session_status(str(self.session_id))
        except Exception:
            return None
    
    def get_controls_help(self) -> str:
        """Get controls help text."""
        return """Available Commands:
  1 - Company 1 pricing     2 - Company 2 pricing     3 - Company 3 pricing
  summary - Show summary    help - Show help          refresh - Refresh display"""
    
    def handle_command(self, command: str) -> None:
        """Handle user commands using CLIInterface."""
        if command in ["1", "2", "3"]:
            company_num = int(command)
            self._handle_company_input(company_num)
        elif command == "help":
            self._show_help()
        elif command == "summary":
            self._show_summary()
        elif command == "refresh":
            self.refresh_data()
    
    def _handle_company_input(self, company_num: int):
        """Starts the process for inputting price and shares for one company."""
        company_terms = GameConfiguration.get_company_terms(company_num)
        price_key = company_terms['price']
        shares_key = company_terms['shares']
        
        company_name = f"Company {company_num}"
        self.console.print(f"\n[bold cyan]Input data for {company_name}:[/bold cyan]")
        
        current_data = self._get_team_data()
        if current_data:
            current_price = current_data.term_values.get(price_key)
            current_shares = current_data.term_values.get(shares_key)
            if current_price:
                self.console.print(f"Current Price: {current_price}")
            if current_shares:
                self.console.print(f"Current Shares: {current_shares}")
        
        try:
            self.cli.handle_team1_input(price_key)
            
            self.cli.handle_team1_input(shares_key)
            
            self.console.print(f"[green]✅ {company_name} data updated successfully![/green]")
            self.refresh_data()
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold cyan]Company Pricing Commands:[/bold cyan]

[cyan]1[/cyan] - Input/edit Company 1 pricing
[cyan]2[/cyan] - Input/edit Company 2 pricing  
[cyan]3[/cyan] - Input/edit Company 3 pricing
[cyan]summary[/cyan] - Show detailed session summary
[cyan]refresh[/cyan] - Refresh display
[cyan]help[/cyan] - Show this help

[bold yellow]Instructions:[/bold yellow]
Set price and shares for each company using enterprise validation.
Team 2 will submit investment bids based on your pricing.
        """
        self.console.print(Panel(help_text, title="Help", style="yellow"))
    
    def _show_summary(self):
        """Shows the big summary screen. This one has a live-refresh loop until the user exits."""
        if not self.current_data:
            self.console.print("[yellow]No session data available[/yellow]")
            return
        
        last_data_hash = None
        
        while True:
            try:
                self.refresh_data()
                
                game_service = self.container.game_service()
                summary_data = game_service.calculate_game2_summary(str(self.session_id))
                
                data_hash = str({
                    'pricing': self._get_team_pricing_data(),
                    'bids': summary_data.get('team2_bids', {}),
                    'companies': summary_data.get('companies', {}),
                    'approvals': {
                        f'company{i}': str(game_service.get_approval_status(str(self.session_id), 
                                         getattr(TermKey, f'COMPANY{i}_DEAL_APPROVAL')))
                        for i in range(1, 4)
                    }
                })
                
                if data_hash != last_data_hash or last_data_hash is None:
                    last_data_hash = data_hash
                    
                    summary_text = f"""
[bold cyan]Session Summary (Live):[/bold cyan]

Session ID: {self.session_id}
Team: Company Pricing Team (Team 1)
Game: {GameConfiguration.get_game_metadata(GameType.GAME_2).name}

[bold yellow]Your Pricing (Team 1):[/bold yellow]
"""
                    
                    pricing_data = self._get_team_pricing_data()
                    for i in range(1, 4):
                        price = pricing_data.get(f'company{i}_price', 'Not set')
                        shares = pricing_data.get(f'company{i}_shares', 'Not set')
                        summary_text += f"\nCompany {i}: Price {price}, Shares {shares}"
                    
                    if summary_data.get('team2_bids'):
                        summary_text += "\n\n[bold magenta]Team 2 Investment Bids:[/bold magenta]"
                        team2_bids = summary_data['team2_bids']
                        for investor_num in range(1, 4):
                            investor_key = f'investor{investor_num}'
                            investor_bids = team2_bids.get(investor_key, {})
                            bids_text = ", ".join([f"C{i+1}:{investor_bids.get(f'company{i+1}', 0) or 'Not set'}" 
                                                 for i in range(3)])
                            summary_text += f"\nInvestor {investor_num}: {bids_text}"
                    
                    if summary_data.get('companies'):
                        summary_text += "\n\n[bold green]Summary Calculations:[/bold green]"
                        companies = summary_data['companies']
                        
                        summary_text += "\n\n[cyan]Shares Bid For:[/cyan]"
                        for i in range(1, 4):
                            company_data = companies.get(f'company{i}', {})
                            shares_bid = company_data.get('shares_bid_for', 0)
                            summary_text += f"\nCompany {i}: {shares_bid}"
                        
                        summary_text += "\n\n[cyan]Capital Raised:[/cyan]"
                        for i in range(1, 4):
                            company_data = companies.get(f'company{i}', {})
                            capital_raised = company_data.get('capital_raised', 'N/A')
                            summary_text += f"\nCompany {i}: {capital_raised}"
                        
                        summary_text += "\n\n[cyan]Subscription Status:[/cyan]"
                        for i in range(1, 4):
                            company_data = companies.get(f'company{i}', {})
                            subscription = company_data.get('subscription', 'N/A')
                            summary_text += f"\nCompany {i}: {subscription}"
                        
                        most_bids = summary_data.get('most_bids_company', 'No data')
                        summary_text += f"\n\n[bold yellow]Which company received the most bids?[/bold yellow]\n{most_bids}"
                    
                    approval_status = game_service.get_approval_status(str(self.session_id), TermKey.COMPANY1_DEAL_APPROVAL)
                    if approval_status is not None:
                        summary_text += "\n\n[bold cyan]Deal Approval Status (Team 2 Controls):[/bold cyan]"
                        
                        for company_num in range(1, 4):
                            deal_approval_key = getattr(TermKey, f'COMPANY{company_num}_DEAL_APPROVAL')
                            status = game_service.get_approval_status(str(self.session_id), deal_approval_key)
                            
                            if status and status.value == "ok":
                                status_display = "[green]APPROVED[/green]"
                            else:
                                status_display = "[yellow]TBD[/yellow]"
                            
                            summary_text += f"\nCompany {company_num}: {status_display}"
                        
                        summary_text += "\n\n[dim]Note: Only Team 2 can approve deals[/dim]"
                    
                    summary_text += "\n\n[dim]Press 'back' to return to main menu[/dim]"
                    
                    self.console.clear()
                    self.console.print(Panel(summary_text, title="Live Summary", style="green"))
                
                try:
                    import sys
                    import select
                    
                    ready, _, _ = select.select([sys.stdin], [], [], 2.0)
                    if ready:
                        user_input = sys.stdin.readline().strip().lower()
                        if user_input in ['back', 'exit', 'q', 'b']:
                            return
                        
                except (EOFError, KeyboardInterrupt):
                    return
                
                status_dto = game_service.get_session_status(str(self.session_id))
                if status_dto and status_dto.is_complete:
                    self.console.print("\n[bold green]🎉 Game Complete! Returning to main menu...[/bold green]")
                    return
                    
            except Exception as e:
                self.console.print(f"[red]Error in summary: {e}[/red]")
                return 