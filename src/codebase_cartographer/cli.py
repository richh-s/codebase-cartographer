import typer

app = typer.Typer(name="codebase-cartographer", help="Codebase Cartographer CLI")

@app.command()
def hello(name: str = "World"):
    """
    Say hello to the specified name.
    """
    typer.echo(f"Hello {name}!")

if __name__ == "__main__":
    app()
