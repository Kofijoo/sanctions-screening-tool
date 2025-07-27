"""CLI commands for data ingestion"""
import typer
from .manager import ListManager

app = typer.Typer(help="Sanctions list data ingestion commands")

@app.command()
def update():
    """Download and update all sanctions lists"""
    try:
        manager = ListManager()
        list_data = manager.load_all()
        consolidated = manager.consolidate(list_data)
        
        typer.echo(f"✅ Successfully updated sanctions lists")
        typer.echo(f"📊 Total entries: {len(consolidated)}")
        
        for source, df in list_data.items():
            typer.echo(f"   {source}: {len(df)} entries")
            
    except Exception as e:
        typer.echo(f"❌ Update failed: {e}", err=True)
        raise typer.Exit(1)

@app.command()
def status():
    """Show status of current sanctions lists"""
    from ..config import settings
    
    processed_file = settings.DATA_DIR / "processed" / "consolidated_sanctions.csv"
    
    if processed_file.exists():
        import pandas as pd
        df = pd.read_csv(processed_file)
        typer.echo(f"📊 Current sanctions database: {len(df)} entries")
        typer.echo(f"📁 File: {processed_file}")
        typer.echo(f"📅 Last modified: {processed_file.stat().st_mtime}")
    else:
        typer.echo("❌ No sanctions data found. Run 'update' first.")

if __name__ == "__main__":
    app()