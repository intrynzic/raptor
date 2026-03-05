from raptor.core.log import error
from raptor.hooks.registry import HOOK_REGISTRY
import typer


app = typer.Typer(help = "Run Git hooks.")

@app.command(help = "Run a Git hook.")
def run(name: str = typer.Argument(help = "The name of the hook to run.")):
    if not name in HOOK_REGISTRY.keys():
        error(f"Hook '{name}' is not installed!")
        return

    HOOK_REGISTRY[name](None) # Passing none for now since there's no context yet!
