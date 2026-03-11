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
def hydrologist(
    target_dir: str = typer.Argument(".", help="Directory to analyze"),
    output: str = typer.Option(".cartography/lineage.json", "--output", "-o", help="Output JSON path")
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
    lineage_path = os.path.join(target_dir, ".cartography", "lineage.json")
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
    
    lineage_path = os.path.join(target_dir, ".cartography", "lineage.json")
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
def version():
    """Print the version of Codebase Cartographer."""
    typer.echo("0.1.0")

if __name__ == "__main__":
    app()
