import os
import typer
from typing import Optional
from dotenv import load_dotenv
from orchestrator import analyze_repo

load_dotenv()

app = typer.Typer(name="codebase-cartographer", help="Codebase Cartographer CLI")

@app.command()
def analyze(
    repo_path: str = typer.Argument(..., help="Path to the repository to analyze."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Custom output directory"),
    llm: bool = typer.Option(False, "--llm", help="Enable LLM-based semantic analysis"),
    semantic_depth: str = typer.Option("light", "--semantic-depth", help="Depth of semantic analysis (light, deep)"),
    store_embeddings: bool = typer.Option(False, "--store-embeddings", help="Store semantic embeddings in the graph"),
    velocity_days: int = typer.Option(30, "--velocity-days", help="Number of days to look back for git velocity"),
    sql_dialect: str = typer.Option("duckdb", "--sql-dialect", help="SQL dialect for AST parsing (duckdb, snowflake, postgres, etc.)")
):
    """
    Analyzes a codebase and generates architectural & lineage maps.
    """
    if repo_path.startswith("http"):
        print(f"Cloning remote repository: {repo_path}")
        import tempfile
        import subprocess
        tmp_dir = tempfile.mkdtemp()
        try:
            subprocess.run(["git", "clone", repo_path, tmp_dir], check=True)
            repo_path = tmp_dir
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return
        
    if not os.path.exists(repo_path):
        typer.echo(f"Error: Path {repo_path} does not exist.")
        raise typer.Exit(1)
        
    typer.echo(f"Initializing analysis for {repo_path}...")
    results = analyze_repo(
        repo_path, 
        llm_enabled=llm, 
        semantic_depth=semantic_depth, 
        store_embeddings=store_embeddings
    )
    typer.echo(f"Analysis successful!")

@app.command()
def hydrologist(
    target_dir: str = typer.Argument(".", help="Directory to analyze"),
    output: str = typer.Option(".cartography/lineage_graph.json", "--output", "-o", help="Output JSON path")
):
    """
    Run Phase 2: The Hydrologist Agent to extract data lineage.
    """
    from codebase_cartographer.agents.hydrologist import HydrologistAgent
    try:
        agent = HydrologistAgent(target_dir)
        out_path = os.path.join(agent.target_dir, output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        agent.run(output_json=output)
        typer.secho(f"Hydrologist Agent completed successfully. Results saved to {output}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Error executing Hydrologist Agent: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

@app.command()
def lineage(
    node_id: str = typer.Argument(..., help="Node ID to view dependencies for"),
    target_dir: str = typer.Argument(".", help="Directory to analyze")
):
    """
    Shows immediate upstream dependencies and downstream consumers.
    """
    import json
    lineage_path = os.path.join(target_dir, ".cartography", "lineage_graph.json")
    if not os.path.exists(lineage_path):
        typer.secho(f"Lineage file not found at {lineage_path}. Run hydrologist first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
        
    with open(lineage_path, 'r') as f:
        data = json.load(f)
        
    edges = data.get("edges", [])
    
    upstream = []
    downstream = []
    
    for edge in edges:
        if edge["target"] == node_id:
            upstream.append(edge["source"])
        if edge["source"] == node_id:
            downstream.append(edge["target"])
            
    typer.secho(f"{node_id}", fg=typer.colors.CYAN, bold=True)
    if upstream:
        typer.echo("  depends on:")
        for u in upstream:
            typer.echo(f"    - {u}")
    if downstream:
        typer.echo("  produces/affects:")
        for d in downstream:
            typer.echo(f"    - {d}")

@app.command()
def impact(
    node_id: str = typer.Argument(..., help="Node ID to analyze impact for"),
    target_dir: str = typer.Argument(".", help="Directory to analyze")
):
    """
    Trace the lineage impact (blast radius) for a given node across the topological graph.
    """
    import json
    import math
    from collections import deque
    
    lineage_path = os.path.join(target_dir, ".cartography", "lineage_graph.json")
    if not os.path.exists(lineage_path):
        typer.secho(f"Lineage file not found at {lineage_path}. Run hydrologist first.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    
    with open(lineage_path, 'r') as f:
        data = json.load(f)
        
    edges = data.get("edges", [])
    all_nodes = data.get("nodes", {}).get("data", []) + data.get("nodes", {}).get("transformations", [])
    nodes = {n["identity"]: n for n in all_nodes}
    
    queue = deque([(node_id, 0)])
    visited_distances = {}
    
    while queue:
        curr, dist = queue.popleft()
        if curr in visited_distances and visited_distances[curr] <= dist:
            continue
        visited_distances[curr] = dist
        
        for edge in edges:
            if edge["source"] == curr:
                queue.append((edge["target"], dist + 1))
                
    if node_id in visited_distances:
        del visited_distances[node_id]
        
    typer.secho(f"{node_id} affects:", fg=typer.colors.CYAN, bold=True)
    
    total_impact = 0.0
    for n, dist in sorted(visited_distances.items(), key=lambda item: item[1]):
        base_importance = nodes.get(n, {}).get("importance_score", 1)
        # Distance-decay weighting
        decay = 1.0 / math.pow(1.5, dist)
        local_impact = base_importance * decay
        total_impact += local_impact
        typer.echo(f"  {n} (Distance: {dist}, Impact: {local_impact:.1f})")
        
    typer.echo(f"\nTotal Weighted Impact: {total_impact:.1f}")

@app.command()
def query(
    repo_path: str = typer.Argument(".", help="Path to the analyzed repository."),
    question: Optional[str] = typer.Option(None, "--question", "-q", help="Single query to run (non-interactive)."),
):
    """
    Query the codebase knowledge graph using natural language.
    Launches the Navigator Agent in interactive mode if no --question is provided.
    """
    if not os.path.exists(repo_path):
        typer.echo(f"Error: Path {repo_path} does not exist.")
        raise typer.Exit(1)

    catalog_path = os.path.join(repo_path, ".cartography", "catalog.json")
    if not os.path.exists(catalog_path):
        typer.secho(
            "No analysis found. Run 'codebase-cartographer analyze <repo_path>' first.",
            fg=typer.colors.RED
        )
        raise typer.Exit(1)

    from agents.navigator import NavigatorAgent
    navigator = NavigatorAgent(repo_path)

    if question:
        answer = navigator.query(question)
        typer.echo(answer)
    else:
        navigator.interactive()


@app.command()
def serve(
    repo_path: str = typer.Argument(".", help="Path to the analyzed repository."),
    port: int = typer.Option(8370, "--port", "-p", help="Port to run the UI server on."),
    host: str = typer.Option("0.0.0.0", "--host", help="Host to bind to."),
):
    """
    Start the Codebase Cartographer Web UI.
    Opens a browser-based interface for exploring module graphs, lineage, and the Navigator.
    """
    import sys, os
    # Add src to path so server.py can import agents
    src_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, src_dir)

    import server as srv
    srv.REPO_PATH = os.path.abspath(repo_path)

    try:
        import uvicorn
    except ImportError:
        typer.secho("❌  uvicorn not installed. Run: pip install uvicorn", fg=typer.colors.RED)
        raise typer.Exit(1)

    typer.secho(f"🗺️  Codebase Cartographer UI → http://localhost:{port}/", fg=typer.colors.CYAN)
    typer.echo(f"   Repo: {srv.REPO_PATH}")
    uvicorn.run(srv.app, host=host, port=port, log_level="warning")


@app.command()
def version():
    """Print the version of Codebase Cartographer."""
    typer.echo("0.2.0")

if __name__ == "__main__":
    app()
