from importlib.metadata import PackageNotFoundError, version

import typer

from raptor.commands import build, clean, doctor, generate, hook, premake, rebuild, run, setup
from raptor.hooks.loader import load_hooks

app = typer.Typer()


def print_version():
    try:
        typer.echo(version("intrynzic-raptor"))
    except PackageNotFoundError:
        typer.echo("0.0.0")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, ver: bool = typer.Option(None, "--version", help="Show the version and exit.", is_eager=True)):
    if ver:
        print_version()
        raise typer.Exit()

    # Show help if no subcommand provided
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(1)

    # Load raptor hooks
    if ctx.invoked_subcommand in ["setup", "doctor", "hook"]:
        load_hooks()


app.add_typer(build.app, name="build", no_args_is_help=True)
app.add_typer(clean.app, name="clean", no_args_is_help=True)
app.add_typer(doctor.app, name="doctor", no_args_is_help=True)
app.add_typer(generate.app, name="generate", no_args_is_help=True)
app.add_typer(hook.app, name="hook", no_args_is_help=True)
app.add_typer(premake.app, name="premake", no_args_is_help=True)
app.add_typer(rebuild.app, name="rebuild", no_args_is_help=True)
app.add_typer(run.app, name="run", no_args_is_help=True)
app.add_typer(setup.app, name="setup", no_args_is_help=True)

if __name__ == "__main__":
    app()
