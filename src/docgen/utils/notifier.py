"""Notification system for completion alerts."""

import sys
import logging
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

logger = logging.getLogger(__name__)


class Notifier:
    """Handle completion notifications for documentation generation."""
    
    def __init__(self, config):
        """Initialize the notifier."""
        self.config = config
        self.console = Console()
    
    def notify_completion(
        self,
        project_name: str,
        summary: Optional[str] = None,
        stats: Optional[dict] = None,
        sound_enabled: bool = True
    ):
        """Send a completion notification."""
        # Play system bell/sound if enabled
        if sound_enabled and self.config.get('notifications', 'enable_sound', default=True):
            self._play_terminal_bell()
        
        # Display colored completion message
        self._display_completion_message(project_name, summary, stats)
    
    def _play_terminal_bell(self):
        """Play terminal bell sound."""
        try:
            # ASCII bell character
            sys.stdout.write('\a')
            sys.stdout.flush()
            logger.debug("Played terminal bell")
        except Exception as e:
            logger.debug(f"Could not play terminal bell: {e}")
    
    def _display_completion_message(
        self,
        project_name: str,
        summary: Optional[str] = None,
        stats: Optional[dict] = None
    ):
        """Display a colorful completion message."""
        message_lines = []
        
        message_lines.append(f"[bold green]✓ Documentation Complete![/bold green]")
        message_lines.append(f"\n[cyan]Project:[/cyan] [bold]{project_name}[/bold]")
        
        if summary:
            message_lines.append(f"\n[dim]{summary}[/dim]")
        
        if stats:
            message_lines.append("\n[bold]Statistics:[/bold]")
            if 'files' in stats:
                message_lines.append(f"  • Files documented: [green]{stats['files']}[/green]")
            if 'lines' in stats:
                message_lines.append(f"  • Lines of code: [green]{stats['lines']:,}[/green]")
            if 'languages' in stats:
                message_lines.append(f"  • Languages: [cyan]{', '.join(stats['languages'][:3])}[/cyan]")
            if 'duration' in stats:
                message_lines.append(f"  • Time taken: [yellow]{stats['duration']:.1f}s[/yellow]")
        
        message_lines.append("\n[bold green]🎉 All documentation files have been generated![/bold green]")
        
        panel = Panel(
            '\n'.join(message_lines),
            border_style="green",
            title="[bold]Documentation Generator[/bold]",
            title_align="left"
        )
        
        self.console.print("\n")
        self.console.print(panel)
        self.console.print()
    
    def notify_error(self, error_message: str):
        """Send an error notification."""
        panel = Panel(
            f"[bold red]Error:[/bold red] {error_message}",
            border_style="red",
            title="[bold]Documentation Generator[/bold]"
        )
        self.console.print("\n")
        self.console.print(panel)
        self.console.print()
    
    def notify_warning(self, warning_message: str):
        """Send a warning notification."""
        self.console.print(f"\n[yellow]⚠ Warning:[/yellow] {warning_message}\n")
