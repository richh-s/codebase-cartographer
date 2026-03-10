import os
import typer
from codebase_cartographer.agents.surveyor import SurveyorAgent

app = typer.Typer(name="codebase-cartographer", help="Codebase Cartographer CLI")

@app.command()
def survey(
    target_dir: str = typer.Argument(".", help="Directory to analyze"),
    output: str = typer.Option(".cartography/module_graph.json", "--output", "-o", help="Output JSON path")
):
    """
    Run Phase 1: The Surveyor Agent to extract the structural graph of the target directory.
    """
    try:
        agent = SurveyorAgent(target_dir)
        # Ensure output directory exists before running
        out_path = os.path.join(agent.target_dir, output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        agent.run(output_json=output)
    except Exception as e:
        typer.secho(f"Error executing Surveyor Agent: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def version():
    """Print the version of Codebase Cartographer."""
    typer.echo("0.1.0")

if __name__ == "__main__":
    app()
