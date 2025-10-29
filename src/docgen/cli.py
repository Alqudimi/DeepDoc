"""Command-line interface for the documentation generator."""

import sys
import logging
from pathlib import Path
from typing import Optional
import argparse

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.logging import RichHandler
from rich import print as rprint

from .core.config import Config
from .core.scanner import ProjectScanner
from .core.llm_client import LLMClient
from .core.workflow import DocumentationWorkflow
from .generators.doc_writer import DocumentationWriter

console = Console()


class DocumentationCLI:
    """Command-line interface for documentation generation."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.config = None
        self.console = console
    
    def run(self, args: Optional[list] = None):
        """Run the CLI application."""
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        self._setup_logging(parsed_args.verbose)
        
        self.console.print(Panel.fit(
            "[bold cyan]AI Documentation Generator[/bold cyan]\n"
            "[dim]Powered by Ollama, LangChain, and LangGraph[/dim]",
            border_style="cyan"
        ))
        
        if parsed_args.command == 'generate':
            self._run_generation(parsed_args)
        elif parsed_args.command == 'init':
            self._init_config()
        else:
            parser.print_help()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description='Generate comprehensive documentation for any project using local AI',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='Enable verbose logging'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Commands')
        
        gen_parser = subparsers.add_parser('generate', help='Generate documentation')
        gen_parser.add_argument(
            'path',
            nargs='?',
            help='Path to the project directory (default: current directory)'
        )
        gen_parser.add_argument(
            '-c', '--config',
            help='Path to config file (default: config.yaml)'
        )
        gen_parser.add_argument(
            '-o', '--output',
            help='Output directory for documentation (default: from config)'
        )
        gen_parser.add_argument(
            '-m', '--model',
            help='Ollama model to use (overrides config)'
        )
        gen_parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing documentation files'
        )
        
        subparsers.add_parser('init', help='Initialize configuration file')
        
        return parser
    
    def _setup_logging(self, verbose: bool):
        """Set up logging configuration."""
        level = logging.DEBUG if verbose else logging.INFO
        
        logging.basicConfig(
            level=level,
            format="%(message)s",
            handlers=[RichHandler(console=self.console, rich_tracebacks=True)]
        )
    
    def _init_config(self):
        """Initialize configuration file."""
        config_path = Path('config.yaml')
        example_path = Path('config.example.yaml')
        
        if config_path.exists():
            overwrite = Confirm.ask(
                f"[yellow]config.yaml already exists. Overwrite?[/yellow]",
                default=False
            )
            if not overwrite:
                self.console.print("[green]Keeping existing config.yaml[/green]")
                return
        
        if example_path.exists():
            import shutil
            shutil.copy(example_path, config_path)
            self.console.print(f"[green]✓[/green] Created config.yaml from template")
        else:
            Config().save(str(config_path))
            self.console.print(f"[green]✓[/green] Created default config.yaml")
        
        self.console.print("\n[cyan]Edit config.yaml to customize documentation generation.[/cyan]")
    
    def _run_generation(self, args):
        """Run documentation generation."""
        project_path = Path(args.path or '.').resolve()
        
        if not project_path.exists():
            self.console.print(f"[red]✗[/red] Project path does not exist: {project_path}")
            sys.exit(1)
        
        if not project_path.is_dir():
            self.console.print(f"[red]✗[/red] Project path is not a directory: {project_path}")
            sys.exit(1)
        
        self.console.print(f"\n[cyan]Project:[/cyan] {project_path}")
        self.console.print(f"[cyan]Directory:[/cyan] {project_path.name}\n")
        
        self.config = Config(args.config)
        
        if args.model:
            self.config.set('ollama', 'model', value=args.model)
        
        if args.output:
            self.config.set('output', 'docs_directory', value=args.output)
        
        if args.overwrite:
            self.config.set('output', 'overwrite_existing', value=True)
        
        proceed = Confirm.ask(
            "[yellow]Generate documentation for this project?[/yellow]",
            default=True
        )
        
        if not proceed:
            self.console.print("[dim]Cancelled by user[/dim]")
            return
        
        self._check_ollama_connection()
        
        try:
            self._generate_documentation(str(project_path))
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(0)
        except Exception as e:
            self.console.print(f"\n[red]✗ Error:[/red] {e}")
            if args.verbose:
                raise
            sys.exit(1)
    
    def _check_ollama_connection(self):
        """Check if Ollama is accessible."""
        if not self.config:
            return
        base_url = self.config.get('ollama', 'base_url')
        model = self.config.get('ollama', 'model')
        
        self.console.print(f"[dim]Ollama URL: {base_url}[/dim]")
        self.console.print(f"[dim]Model: {model}[/dim]\n")
        
        try:
            import requests
            response = requests.get(base_url, timeout=5)
            if response.status_code == 200:
                self.console.print("[green]✓[/green] Ollama connection successful\n")
            else:
                self.console.print("[yellow]⚠[/yellow] Ollama server responded with unexpected status\n")
        except Exception as e:
            self.console.print(
                f"[red]✗[/red] Cannot connect to Ollama at {base_url}\n"
                f"[yellow]Please ensure Ollama is running:[/yellow]\n"
                f"  • Install: https://ollama.ai\n"
                f"  • Start: ollama serve\n"
                f"  • Pull model: ollama pull {model}\n"
            )
            sys.exit(1)
    
    def _generate_documentation(self, project_path: str):
        """Generate documentation with progress tracking."""
        import time
        from ..utils.notifier import Notifier
        
        start_time = time.time()
        
        scanner = ProjectScanner(self.config)
        llm_client = LLMClient(self.config)
        workflow = DocumentationWorkflow(scanner, llm_client, self.config)
        writer = DocumentationWriter(self.config)
        notifier = Notifier(self.config)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            
            task = progress.add_task("[cyan]Generating documentation...", total=8)
            
            progress.update(task, description="[cyan]Analyzing project...")
            state = workflow.run(project_path)
            
            if state.get('status') == 'error':
                self.console.print(f"[red]✗ Error:[/red] {state.get('error')}")
                notifier.notify_error(state.get('error', 'Unknown error'))
                return
            
            progress.update(task, advance=7)
            progress.update(task, description="[cyan]Writing documentation files...")
            
            written_files = writer.write_documentation(project_path, state)
            progress.update(task, advance=1, description="[green]✓ Documentation complete!")
        
        duration = time.time() - start_time
        
        # Send completion notification
        analysis = state.get('analysis', {})
        stats = {
            'files': analysis.get('total_files', 0),
            'lines': analysis.get('total_lines', 0),
            'languages': list(analysis.get('languages', {}).keys()),
            'duration': duration
        }
        
        notifier.notify_completion(
            project_name=analysis.get('name', 'Project'),
            summary=state.get('summary', ''),
            stats=stats
        )
        
        self._display_results(state, written_files)
    
    def _display_results(self, state, written_files: dict):
        """Display generation results."""
        analysis = state.get('analysis', {})
        
        self.console.print("\n[bold green]✓ Documentation Generated Successfully![/bold green]\n")
        
        stats_table = Table(title="Project Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")
        
        stats_table.add_row("Total Files", str(analysis.get('total_files', 0)))
        stats_table.add_row("Lines of Code", str(analysis.get('total_lines', 0)))
        stats_table.add_row("Languages", ', '.join(list(analysis.get('languages', {}).keys())[:5]))
        stats_table.add_row("Frameworks", ', '.join(analysis.get('frameworks', [])) or 'None')
        
        self.console.print(stats_table)
        
        self.console.print("\n[bold]Generated Files:[/bold]")
        for filename in sorted(written_files.keys()):
            self.console.print(f"  [green]✓[/green] {filename}")
        
        self.console.print(
            "\n[dim]Tip: Review and customize the generated documentation as needed.[/dim]"
        )


def main():
    """Entry point for the CLI."""
    cli = DocumentationCLI()
    cli.run()


if __name__ == '__main__':
    main()
