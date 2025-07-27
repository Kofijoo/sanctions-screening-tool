"""Enhanced main entry point with professional interface options"""
import typer
from rich.console import Console
from rich.panel import Panel

# Import interface components
from .interface.cli.commands import app as cli_app
from .interface.api.endpoints import app as api_app

console = Console()
main_app = typer.Typer(help="🛡️ SLST - Professional Sanctions Screening System")

# Add CLI commands as subcommand
main_app.add_typer(cli_app, name="cli", help="Command-line interface")

@main_app.command()
def web(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    reload: bool = typer.Option(False, help="Enable auto-reload for development")
):
    """Start the web API server and dashboard"""
    
    console.print(Panel(
        "[bold green]🚀 Starting SLST Web Server[/bold green]\n\n"
        f"[cyan]API Documentation:[/cyan] http://{host}:{port}/docs\n"
        f"[cyan]Dashboard:[/cyan] http://{host}:{port}/\n"
        f"[cyan]System Status:[/cyan] http://{host}:{port}/status\n\n"
        "[yellow]Press Ctrl+C to stop[/yellow]",
        title="SLST Web Server",
        border_style="green"
    ))
    
    try:
        import uvicorn
        uvicorn.run(
            "app.interface.api.endpoints:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except ImportError:
        console.print("❌ uvicorn not installed. Install with: pip install uvicorn", style="red")
        raise typer.Exit(1)

@main_app.command()
def demo():
    """Run interactive demo of SLST capabilities"""
    
    console.print(Panel(
        "[bold blue]🎬 SLST Interactive Demo[/bold blue]\n\n"
        "This demo will showcase the key features of the\n"
        "Sanctions List Screening Tool (SLST)",
        title="Demo Mode",
        border_style="blue"
    ))
    
    # Import and run the existing demo
    from tests.test_data import create_sample_sanctions_data
    from app.preprocessing.processor import NameProcessor
    from app.matching.engine import MatchingEngine
    from app.flagging.engine import FlaggingEngine
    
    processor = NameProcessor()
    matching_engine = MatchingEngine()
    flagging_engine = FlaggingEngine()
    
    # Prepare data
    sanctions_df = create_sample_sanctions_data()
    sanctions_df = processor.process_dataframe(sanctions_df)
    
    demo_queries = [
        ("Osama bin Laden", "Known terrorist - should be blocked"),
        ("Al Qaeda", "Terrorist organization - high risk"),
        ("John Smith", "Common name - may have matches"),
        ("Jane Doe", "Clean name - should auto-clear")
    ]
    
    for query, description in demo_queries:
        console.print(f"\n🔍 [bold]Testing:[/bold] '{query}' [dim]({description})[/dim]")
        
        # Screen the name
        screening_result = matching_engine.screen_name(query, sanctions_df)
        final_result = flagging_engine.process_screening_result(screening_result)
        
        # Display result
        decision = final_result['decision']['action']
        risk = final_result['summary']['highest_risk']
        matches = len(final_result['matches'])
        
        decision_color = {
            'BLOCK': 'red',
            'ESCALATE': 'yellow', 
            'MANUAL_REVIEW': 'blue',
            'AUTO_CLEAR': 'green'
        }.get(decision, 'white')
        
        console.print(f"   📊 Matches: {matches}")
        console.print(f"   ⚖️  Decision: [{decision_color}]{decision}[/{decision_color}]")
        console.print(f"   🚨 Risk Level: {risk}")
        
        if final_result['matches']:
            best_match = final_result['matches'][0]
            console.print(f"   🎯 Best Match: {best_match['target_name']} ({best_match['source']})")
    
    console.print(Panel(
        "[bold green]✨ Demo completed successfully![/bold green]\n\n"
        "[cyan]Next steps:[/cyan]\n"
        "• Run '[bold]slst web[/bold]' to start the web interface\n"
        "• Use '[bold]slst cli screen \"Name\"[/bold]' for CLI screening\n"
        "• Check '[bold]slst cli status[/bold]' for system health",
        title="Demo Complete",
        border_style="green"
    ))

@main_app.command()
def info():
    """Show system information and capabilities"""
    
    console.print(Panel(
        "[bold blue]🛡️ SLST - Sanctions List Screening Tool[/bold blue]\n\n"
        "[bold]Version:[/bold] 1.0.0\n"
        "[bold]Purpose:[/bold] Production-grade compliance screening\n\n"
        "[bold cyan]Key Features:[/bold cyan]\n"
        "• Multi-source sanctions list ingestion (OFAC, UN, HMT, EU)\n"
        "• Advanced fuzzy matching with transliteration support\n"
        "• Risk-based scoring and automated decision making\n"
        "• Full audit trail and compliance reporting\n"
        "• Professional web dashboard and CLI interface\n"
        "• REST API for system integration\n\n"
        "[bold cyan]Interfaces Available:[/bold cyan]\n"
        "• [green]Web Dashboard[/green] - Modern analyst interface\n"
        "• [green]CLI Tools[/green] - Enterprise command-line operations\n"
        "• [green]REST API[/green] - Integration endpoints\n"
        "• [green]Batch Processing[/green] - High-volume screening\n\n"
        "[bold yellow]Built for:[/bold yellow] Banks, Fintechs, Compliance Teams",
        title="System Information",
        border_style="blue"
    ))

if __name__ == "__main__":
    main_app()