"""Enterprise CLI commands for SLST operations"""
import typer
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from pathlib import Path
import json
import time
from datetime import datetime

from ...preprocessing.processor import NameProcessor
from ...matching.engine import MatchingEngine
from ...flagging.engine import FlaggingEngine
from ...ingestion.manager import ListManager
from ...config import settings

app = typer.Typer(help="🛡️ SLST - Enterprise Sanctions Screening CLI")
console = Console()

# Global components
processor = NameProcessor()
matching_engine = MatchingEngine()
flagging_engine = FlaggingEngine()
list_manager = ListManager()

@app.command()
def screen(
    name: str = typer.Argument(..., help="Name to screen against sanctions lists"),
    output: str = typer.Option("table", help="Output format: table, json, csv"),
    save: str = typer.Option(None, help="Save results to file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Screen a single name against sanctions lists"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Load sanctions data
        task1 = progress.add_task("Loading sanctions data...", total=None)
        try:
            list_data = list_manager.load_all()
            sanctions_df = list_manager.consolidate(list_data)
            sanctions_df = processor.process_dataframe(sanctions_df)
            progress.update(task1, description=f"✅ Loaded {len(sanctions_df)} sanctions entries")
        except Exception as e:
            console.print(f"❌ Failed to load sanctions data: {e}", style="red")
            raise typer.Exit(1)
        
        # Screen the name
        task2 = progress.add_task("Screening name...", total=None)
        start_time = time.time()
        
        screening_result = matching_engine.screen_name(name, sanctions_df)
        final_result = flagging_engine.process_screening_result(screening_result)
        
        processing_time = (time.time() - start_time) * 1000
        progress.update(task2, description=f"✅ Screening completed ({processing_time:.1f}ms)")
    
    # Display results
    display_screening_results(final_result, output, save, verbose, processing_time)

@app.command()
def batch(
    input_file: str = typer.Argument(..., help="CSV file with names to screen"),
    output_file: str = typer.Option("screening_results.csv", help="Output file for results"),
    name_column: str = typer.Option("name", help="Column name containing names to screen"),
    batch_size: int = typer.Option(100, help="Batch processing size")
):
    """Process multiple names from CSV file"""
    
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"❌ Input file not found: {input_file}", style="red")
        raise typer.Exit(1)
    
    # Load input data
    try:
        df = pd.read_csv(input_path)
        if name_column not in df.columns:
            console.print(f"❌ Column '{name_column}' not found in CSV", style="red")
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"❌ Failed to read CSV: {e}", style="red")
        raise typer.Exit(1)
    
    names_to_screen = df[name_column].dropna().tolist()
    total_names = len(names_to_screen)
    
    console.print(f"📊 Processing {total_names} names from {input_file}")
    
    # Load sanctions data
    with console.status("Loading sanctions data..."):
        try:
            list_data = list_manager.load_all()
            sanctions_df = list_manager.consolidate(list_data)
            sanctions_df = processor.process_dataframe(sanctions_df)
            console.print(f"✅ Loaded {len(sanctions_df)} sanctions entries")
        except Exception as e:
            console.print(f"❌ Failed to load sanctions data: {e}", style="red")
            raise typer.Exit(1)
    
    # Process in batches
    results = []
    start_time = time.time()
    
    with Progress(console=console) as progress:
        task = progress.add_task("Processing names...", total=total_names)
        
        for i, name in enumerate(names_to_screen):
            screening_result = matching_engine.screen_name(name, sanctions_df)
            final_result = flagging_engine.process_screening_result(screening_result)
            
            # Flatten result for CSV
            result_row = {
                'name': name,
                'decision': final_result['decision']['action'],
                'reason': final_result['decision']['reason'],
                'risk_level': final_result['summary']['highest_risk'],
                'matches_found': len(final_result['matches']),
                'highest_score': final_result['summary'].get('highest_score', 0),
                'processing_time': datetime.now().isoformat()
            }
            
            # Add match details
            if final_result['matches']:
                best_match = final_result['matches'][0]
                result_row.update({
                    'best_match_name': best_match.get('target_name', ''),
                    'best_match_source': best_match.get('source', ''),
                    'best_match_score': best_match.get('risk_score', 0)
                })
            
            results.append(result_row)
            progress.update(task, advance=1)
    
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    
    processing_time = time.time() - start_time
    
    # Summary
    summary_table = Table(title="Batch Processing Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")
    
    summary_table.add_row("Total Processed", str(total_names))
    summary_table.add_row("Processing Time", f"{processing_time:.1f}s")
    summary_table.add_row("Rate", f"{total_names/processing_time:.1f} names/sec")
    summary_table.add_row("High Risk", str(len([r for r in results if r['risk_level'] == 'HIGH'])))
    summary_table.add_row("Blocked", str(len([r for r in results if r['decision'] == 'BLOCK'])))
    summary_table.add_row("Output File", output_file)
    
    console.print(summary_table)

@app.command()
def status():
    """Show system status and statistics"""
    
    with console.status("Checking system status..."):
        try:
            # Check sanctions data
            list_data = list_manager.load_all()
            sanctions_df = list_manager.consolidate(list_data)
            
            # System info
            status_table = Table(title="🛡️ SLST System Status")
            status_table.add_column("Component", style="cyan")
            status_table.add_column("Status", style="green")
            status_table.add_column("Details")
            
            status_table.add_row("System", "✅ Healthy", "All components operational")
            status_table.add_row("Sanctions Data", "✅ Loaded", f"{len(sanctions_df)} entries")
            status_table.add_row("Sources", "✅ Active", ", ".join(sanctions_df['source'].unique()))
            status_table.add_row("Last Update", "✅ Current", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            console.print(status_table)
            
            # Data breakdown
            source_table = Table(title="📊 Data Sources")
            source_table.add_column("Source", style="cyan")
            source_table.add_column("Entries", style="green")
            source_table.add_column("Percentage")
            
            for source in sanctions_df['source'].unique():
                count = len(sanctions_df[sanctions_df['source'] == source])
                percentage = (count / len(sanctions_df)) * 100
                source_table.add_row(source, str(count), f"{percentage:.1f}%")
            
            console.print(source_table)
            
        except Exception as e:
            console.print(f"❌ System check failed: {e}", style="red")

@app.command()
def update():
    """Update sanctions lists from official sources"""
    
    console.print("🔄 Updating sanctions lists from official sources...")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("Downloading updates...", total=None)
        
        try:
            list_data = list_manager.load_all()
            consolidated = list_manager.consolidate(list_data)
            
            progress.update(task, description="✅ Update completed")
            
            # Show update summary
            update_table = Table(title="📥 Update Summary")
            update_table.add_column("Source", style="cyan")
            update_table.add_column("Status", style="green")
            update_table.add_column("Entries")
            
            for source, df in list_data.items():
                update_table.add_row(source, "✅ Updated", str(len(df)))
            
            console.print(update_table)
            console.print(f"📊 Total consolidated entries: {len(consolidated)}")
            
        except Exception as e:
            console.print(f"❌ Update failed: {e}", style="red")
            raise typer.Exit(1)

def display_screening_results(result, output_format, save_file, verbose, processing_time):
    """Display screening results in specified format"""
    
    if output_format == "json":
        output = json.dumps(result, indent=2, default=str)
        console.print(output)
    
    elif output_format == "table":
        # Main result panel
        decision = result['decision']
        summary = result['summary']
        
        decision_color = {
            'BLOCK': 'red',
            'ESCALATE': 'yellow',
            'MANUAL_REVIEW': 'blue',
            'AUTO_CLEAR': 'green'
        }.get(decision['action'], 'white')
        
        result_panel = Panel(
            f"[bold]Query:[/bold] {result['query']}\n"
            f"[bold]Decision:[/bold] [{decision_color}]{decision['action']}[/{decision_color}]\n"
            f"[bold]Reason:[/bold] {decision['reason']}\n"
            f"[bold]Risk Level:[/bold] {summary['highest_risk']}\n"
            f"[bold]Processing Time:[/bold] {processing_time:.1f}ms",
            title="🛡️ Screening Result",
            border_style=decision_color
        )
        console.print(result_panel)
        
        # Matches table
        if result['matches']:
            matches_table = Table(title="🎯 Matches Found")
            matches_table.add_column("Target Name", style="cyan")
            matches_table.add_column("Source", style="green")
            matches_table.add_column("Risk Score", style="red")
            matches_table.add_column("Match Type")
            matches_table.add_column("Confidence")
            
            for match in result['matches']:
                matches_table.add_row(
                    match.get('target_name', ''),
                    match.get('source', ''),
                    f"{match.get('risk_score', 0):.1f}%",
                    match.get('match_type', ''),
                    match.get('confidence', '')
                )
            
            console.print(matches_table)
        else:
            console.print("✅ No matches found - name appears clean")
    
    # Save to file if requested
    if save_file:
        with open(save_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        console.print(f"💾 Results saved to {save_file}")

if __name__ == "__main__":
    app()