from typing import List, Optional

import typer

from raptor.core.log import error
from raptor.hooks.registry import HOOK_REGISTRY

app = typer.Typer(help="Run Git hooks.")


@app.command(help="Run a Git hook.")
def run(
    name: str = typer.Argument(help="The name of the hook to run."),
    args: Optional[List[str]] = typer.Argument(None, help="Arguments passed from Git.")
):
    if name not in HOOK_REGISTRY.keys():
        error(f"Hook '{name}' is not installed!")
        return

    HOOK_REGISTRY[name](args)
