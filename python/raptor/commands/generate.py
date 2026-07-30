import typer

from raptor.core.log import critical, info
from raptor.config.loader import CONFIG


app = typer.Typer(help=f"Generate and manage project files using {CONFIG.metabuild.generator}.")


# TODO: Wire this function in properly!
def main():
    pass


# @app.command(help="Generate IntricateEngine GUIDs.", no_args_is_help=True)
# def guid(
#     count: int = typer.Option(1, "--count", "-c", help="The number of GUIDs to generate."),
#     builtin: bool = typer.Option(False, "--builtin", "-b", help="Generate GUIDs following Intricate's pattern for built-in GUIDs."),
#     length: int = typer.Option(32, "--length", "-l", help="The character-length of the GUIDs to generate."),
# ):
