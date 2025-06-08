from uuid import UUID
from decimal import Decimal
from typing import Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from ...domain.value_objects.team_id import TeamId
from ...domain.value_objects.term_key import TermKey
from ...domain.value_objects.game_type import GameType
from ...domain.services.game_configuration import GameConfiguration
from ...domain.services.term_validation_service import TermValidationService
from ...application.dto.session_status_dto import SessionStatusDTO
from .cli_interface import CLIInterface

class Game2Team2View:
    """The screen for Team 2 in Game 2. They see prices from Team 1 and make bids."""
    
    def __init__(self, container, console: Console):
        self.container = container
        self.console = console
        self.cli = CLIInterface(container, console)
        self.session_id: UUID = None
        self.team_id = TeamId.TEAM_TWO
        self.current_data: Optional[SessionStatusDTO] = None
        self.validation_service = TermValidationService()
        
    def set_session_id(self, session_id: UUID):
        """Set the game session context."""
        self.session_id = session_id
        self.cli.set_context(session_id, self.team_id)
        self.refresh_data()
    
    def refresh_data(self) -> None:
        """Refresh data from backend."""
        self.current_data = self._get_session_status()
    
    def render(self) -> Panel:
        """Render the main interface."""
        pricing_table = self._create_pricing_table()
        bidding_table = self._create_bidding_table()
        content = Group(pricing_table, "", bidding_table)
        
        return Panel(
            content,
            title="💰 Team 2 - Investment Bidding",
            subtitle="Submit bids for company shares",
            style="green"
        )
    
    def _create_pricing_table(self) -> Table:
        """Create Team 1 pricing display table."""
        table = Table(show_header=True, header_style="bold blue", width=80, title="Team 1 Pricing")
        table.add_column("Pricing", style="cyan", width=15)
        table.add_column("Company 1", style="green", width=15)
        table.add_column("Company 2", style="green", width=15) 
        table.add_column("Company 3", style="green", width=15)
        table.add_column("Unit", style="dim", width=10)
        
        team1_pricing = self._get_team1_pricing_data()
        
        table.add_row(
            "Price:",
            team1_pricing.get('company1_price', "[yellow]Waiting...[/yellow]"),
            team1_pricing.get('company2_price', "[yellow]Waiting...[/yellow]"),
            team1_pricing.get('company3_price', "[yellow]Waiting...[/yellow]"),
            "#"
        )
        table.add_row(
            "Shares:",
            team1_pricing.get('company1_shares', "[yellow]Waiting...[/yellow]"),
            team1_pricing.get('company2_shares', "[yellow]Waiting...[/yellow]"),
            team1_pricing.get('company3_shares', "[yellow]Waiting...[/yellow]"),
            "#"
        )
        
        return table
    
    def _create_bidding_table(self) -> Table:
        """Create Team 2 bidding table."""
        table = Table(show_header=True, header_style="bold green", width=80, title="Team 2 Investment Bids")
        table.add_column("Shares Bid", style="cyan", width=15)
        table.add_column("Company 1", style="blue", width=15)
        table.add_column("Company 2", style="blue", width=15) 
        table.add_column("Company 3", style="blue", width=15)
        table.add_column("Unit", style="dim", width=10)
        
        team2_bids = self._get_team2_bids_data()
        
        for investor_num in range(1, 4):
            table.add_row(
                f"Investor {investor_num}:",
                team2_bids.get(f'investor{investor_num}_c1', "[dim]Not set[/dim]"),
                team2_bids.get(f'investor{investor_num}_c2', "[dim]Not set[/dim]"),
                team2_bids.get(f'investor{investor_num}_c3', "[dim]Not set[/dim]"),
                "#"
            )
        
        return table
    
    def _get_team1_pricing_data(self) -> Dict[str, str]:
        """Digs through the session state to get just Team 1 price/shares data."""
        if not self.current_data:
            return {f'company{i}_{field}': "[yellow]Waiting...[/yellow]" for i in range(1, 4) for field in ['price', 'shares']}
        
        team1_data = self._get_team_data(TeamId.TEAM_ONE)
        if not team1_data:
            return {f'company{i}_{field}': "[yellow]Waiting...[/yellow]" for i in range(1, 4) for field in ['price', 'shares']}
        
        result = {}
        for company_num in range(1, 4):
            company_terms = GameConfiguration.get_company_terms(company_num)
            price_key = company_terms['price']
            shares_key = company_terms['shares']
            
            result[f'company{company_num}_price'] = str(team1_data.term_values.get(price_key, "[yellow]Waiting...[/yellow]"))
            result[f'company{company_num}_shares'] = str(team1_data.term_values.get(shares_key, "[yellow]Waiting...[/yellow]"))
        
        return result
    
    def _get_team2_bids_data(self) -> Dict[str, str]:
        """Digs through the session state to get all the bids our team has made."""
        if not self.current_data:
            return {f'investor{i}_c{j}': "[dim]Not set[/dim]" for i in range(1, 4) for j in range(1, 4)}
        
        team2_data = self._get_team_data(TeamId.TEAM_TWO)
        if not team2_data:
            return {f'investor{i}_c{j}': "[dim]Not set[/dim]" for i in range(1, 4) for j in range(1, 4)}
        
        result = {}
        for investor_num in range(1, 4):
            for company_num in range(1, 4):
                term_key = GameConfiguration.get_investor_term(investor_num, company_num)
                value = team2_data.term_values.get(term_key)
                result[f'investor{investor_num}_c{company_num}'] = str(value) if value is not None else "[dim]Not set[/dim]"
        
        return result
    
    def _get_team_data(self, team_id: TeamId):
        """Get team data safely."""
        if not self.current_data or not hasattr(self.current_data, 'team_data'):
            return None
        return self.current_data.team_data.get(team_id)
    
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
  1 - Investor 1 bids       2 - Investor 2 bids       3 - Investor 3 bids
  summary - Show summary    help - Show help          refresh - Refresh display"""
    
    def handle_command(self, command: str) -> None:
        """Handle user commands using CLIInterface."""
        if command in ["1", "2", "3"]:
            investor_num = int(command)
            self._handle_investor_input(investor_num)
        elif command == "help":
            self._show_help()
        elif command == "summary":
            self._show_summary()
        elif command == "refresh":
            self.refresh_data()
    
    def _handle_investor_input(self, investor_num: int):
        """Handle investor bidding input with proper validation."""
        investor_name = f"Investor {investor_num}"
        self.console.print(f"\n[bold cyan]Input bids for {investor_name}:[/bold cyan]")
        
        if not self._is_team1_pricing_complete():
            self.console.print("[yellow]⏳ Waiting for Team 1 to set company pricing...[/yellow]")
            return
        
        current_data = self._get_team_data(TeamId.TEAM_TWO)
        if current_data:
            self.console.print(f"Current bids for {investor_name}:")
            for company_num in range(1, 4):
                term_key = GameConfiguration.get_investor_term(investor_num, company_num)
                current_bid = current_data.term_values.get(term_key)
                if current_bid:
                    self.console.print(f"  Company {company_num}: {current_bid}")
        
        try:
            for company_num in range(1, 4):
                term_key = GameConfiguration.get_investor_term(investor_num, company_num)
                self.cli.handle_team1_input(term_key)
            
            self.console.print(f"[green]✅ {investor_name} bids updated successfully![/green]")
            self.refresh_data()
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
    
    def _is_team1_pricing_complete(self) -> bool:
        """Just checks if Team 1 is done with their part so we can start bidding."""
        team1_pricing = self._get_team1_pricing_data()
        return not any("[yellow]Waiting...[/yellow]" in str(value) for value in team1_pricing.values())
    
    def _show_help(self):
        """Show help information."""
        help_text = """
[bold cyan]Investment Bidding Commands:[/bold cyan]

[cyan]1[/cyan] - Input/edit Investor 1 bids
[cyan]2[/cyan] - Input/edit Investor 2 bids  
[cyan]3[/cyan] - Input/edit Investor 3 bids
[cyan]summary[/cyan] - Show detailed session summary
[cyan]refresh[/cyan] - Refresh display
[cyan]help[/cyan] - Show this help

[bold yellow]Instructions:[/bold yellow]
Wait for Team 1 to set company pricing, then submit bids
for each investor across all three companies using enterprise validation.
        """
        self.console.print(Panel(help_text, title="Help", style="yellow"))
    
    def _show_summary(self):
        """The big summary screen. This is where Team 2 can finalize the round and then approve the deals."""
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
                    'team1_pricing': self._get_team1_pricing_data(),
                    'team2_bids': self._get_team2_bids_data(),
                    'companies': summary_data.get('companies', {}),
                    'approvals': {
                        f'company{i}': str(game_service.get_approval_status(str(self.session_id), 
                                         getattr(TermKey, f'COMPANY{i}_DEAL_APPROVAL')))
                        for i in range(1, 4)
                    },
                    'inputs_filled': self._are_all_inputs_filled()
                })
                
                if data_hash != last_data_hash or last_data_hash is None:
                    last_data_hash = data_hash
                    
                    summary_text = f"""
[bold cyan]Session Summary (Live):[/bold cyan]

Session ID: {self.session_id}
Team: Investment Bidding Team (Team 2)
Game: {GameConfiguration.get_game_metadata(GameType.GAME_2).name}

[bold yellow]Team 1 Pricing:[/bold yellow]
"""
                    
                    team1_pricing = self._get_team1_pricing_data()
                    for i in range(1, 4):
                        price = team1_pricing.get(f'company{i}_price', 'Not set')
                        shares = team1_pricing.get(f'company{i}_shares', 'Not set')
                        summary_text += f"\nCompany {i}: Price {price}, Shares {shares}"
                    
                    summary_text += "\n\n[bold yellow]Team 2 Investment Bids:[/bold yellow]"
                    team2_bids = self._get_team2_bids_data()
                    for i in range(1, 4):
                        summary_text += f"\nInvestor {i}:"
                        for j in range(1, 4):
                            bid = team2_bids.get(f'investor{i}_c{j}', 'Not set')
                            summary_text += f" C{j}:{bid}"
                    
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
                    
                    if not self._are_all_inputs_filled():
                        summary_text += "\n\n[yellow]Summary is preliminary. Not all data has been entered.[/yellow]"
                        summary_text += "\n[dim]Press 'back' to return to main menu[/dim]"
                    elif approval_status is None:
                        summary_text += "\n\n[bold cyan]Ready to finalize round![/bold cyan]"
                        summary_text += "\n[dim]Press 'f' to finalize, 'back' to return to main menu[/dim]"
                    else:
                        summary_text = self._add_final_approvals_to_summary(summary_text, game_service)
                        summary_text += "\n\n[dim]Press 'back' to return, approve1/2/3 to toggle approvals[/dim]"
                    
                    self.console.clear()
                    self.console.print(Panel(summary_text, title="Live Summary", style="green"))
                
                import sys
                import select
                
                ready, _, _ = select.select([sys.stdin], [], [], 2.0) 
                if ready:
                    user_input = sys.stdin.readline().strip().lower()
                    if user_input in ['back', 'exit', 'q', 'b']:
                        return  
                    elif user_input == 'f' and self._are_all_inputs_filled() and approval_status is None:
                        try:
                            game_service.finalize_game2_round(str(self.session_id))
                            self.console.print("[green]✅ Round finalized. Ready for final approvals.[/green]")
                            self.refresh_data()
                        except Exception as e:
                            self.console.print(f"[red]Error finalizing round: {e}[/red]")
                    elif user_input in ["approve1", "approve2", "approve3"] and approval_status is not None:
                        company_num = int(user_input.replace("approve", ""))
                        self._handle_deal_approval(company_num)
                
                status_dto = game_service.get_session_status(str(self.session_id))
                if status_dto and status_dto.is_complete:
                    self.console.print("\n[bold green]🎉 Game Complete! Returning to main menu...[/bold green]")
                    return
                    
            except Exception as e:
                self.console.print(f"[red]Error in summary: {e}[/red]")
                return
    
    def _add_final_approvals_to_summary(self, summary_text: str, game_service) -> str:
        """Add final approvals section to summary text."""
        try:
            summary_text += "\n\n[bold cyan]Final Deal Approvals:[/bold cyan]"
            
            for company_num in range(1, 4):
                deal_approval_key = getattr(TermKey, f'COMPANY{company_num}_DEAL_APPROVAL')
                status = game_service.get_approval_status(str(self.session_id), deal_approval_key)
                
                if status and status.value == "ok":
                    status_display = "[green]APPROVED[/green]"
                else:
                    status_display = "[yellow]TBD[/yellow]"
                
                summary_text += f"\nCompany {company_num}: {status_display}"
            
            return summary_text
            
        except Exception as e:
            summary_text += f"\n[red]Error loading approvals: {e}[/red]"
            return summary_text
    
    def _are_all_inputs_filled(self) -> bool:
        """Checks if everyone has entered their numbers so we can finalize the round."""
        team1_pricing = self._get_team1_pricing_data()
        team2_bids = self._get_team2_bids_data()
        
        for i in range(1, 4):
            if "[yellow]Waiting...[/yellow]" in str(team1_pricing.get(f'company{i}_price', '')):
                return False
            if "[yellow]Waiting...[/yellow]" in str(team1_pricing.get(f'company{i}_shares', '')):
                return False
        
        for i in range(1, 4):
            for j in range(1, 4):
                if "[dim]Not set[/dim]" in str(team2_bids.get(f'investor{i}_c{j}', '')):
                    return False
        
        return True
    
    def _handle_deal_approval(self, company_num: int):
        """Actually toggles the TBD/OK status for one of the final deals."""
        try:
            game_service = self.container.game_service()
            deal_approval_key = getattr(TermKey, f'COMPANY{company_num}_DEAL_APPROVAL')
            
            new_status = game_service.toggle_approval_status(str(self.session_id), deal_approval_key)
            status_text = "APPROVED" if new_status.value == "ok" else "TBD"
            
            self.console.print(f"[green]✅ Company {company_num} deal status: {status_text}[/green]")
            self.refresh_data()
            
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]") 