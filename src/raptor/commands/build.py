from raptor.config.loader import CONFIG
from raptor.core.msbuild import build, clean
import typer


app = typer.Typer(help = "Build the project.")

# Factory function for creating commands for each build-config
def create_build_command(config_name: str):
    def command(
        clean_cfg: bool = typer.Option(False, "--clean", "-c", help = f"Clean the {config_name} configuration before building."),
    ):
        if clean_cfg:
            clean(config_name, CONFIG.workspace.default_arch)

        build(config_name, CONFIG.workspace.default_arch)

    return command

for cfg in CONFIG.workspace.configs:
    app.command(name = cfg, help = f"Build the project for the {cfg} configuration.")(create_build_command(cfg))
