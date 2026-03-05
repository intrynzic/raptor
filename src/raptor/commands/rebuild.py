from raptor.config.loader import CONFIG
from raptor.core.msbuild import rebuild
import typer


app = typer.Typer(help = "Rebuild the project.")

# Factory function for creating commands for each build-config
def create_build_command(config_name: str):
    def command():
        rebuild(config_name, CONFIG.workspace.default_arch)

    return command

for cfg in CONFIG.workspace.configs:
    app.command(name = cfg, help = f"Rebuild the project for the {cfg} configuration.")(create_build_command(cfg))
