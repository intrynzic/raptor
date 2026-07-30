from typing import Optional

import click
import typer

from raptor.build.metabuild import generate
from raptor.config.loader import CONFIG

app = typer.Typer(help=f"Generate and manage project files using {CONFIG.metabuild.generator}.")


@app.callback(invoke_without_command=True)
def main(args: Optional[list[str]] = typer.Argument(None, metavar="ARGS", click_type=click.UNPROCESSED)):
    generate(args)
