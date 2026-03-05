from pathlib import Path

import typer

from raptor.config.loader import CONFIG
from raptor.core.log import error
from raptor.core.msbuild import build, build_and_run, run_project

app = typer.Typer(help="Build and run an executable project.")


# Factory function for creating commands for each executable project
def create_build_command(prj_name: str):
    def command(
        cfg: str = typer.Option(
            CONFIG.workspace.default_config, "--config", "--cfg", help="The project configuration to run.", show_choices=True
        ),
        args: list[str] = typer.Argument(None, help="Extra arguments to pass to the app."),
    ):
        prj = CONFIG.workspace.executable_projects[prj_name]

        if prj.language not in ["cpp", "csharp"]:
            error(f"Unknown project language '{prj.language}' for project '{prj_name}'!")
            return

        if prj.build_mode not in ["project", "solution"]:
            error(f"Unknown project build_mode '{prj.build_mode}' for project '{prj_name}'!")
            return

        prj_path = Path(prj.dir) / f"{prj_name}.{'vcxproj' if prj.language == 'cpp' else 'csproj'}"
        if prj.build_mode == "project":
            build_and_run(prj_path, cfg, prj.arch, args)
        else:
            build(cfg, prj.arch)
            run_project(prj_path, cfg, prj.arch, args)

    return command


for prj_name in CONFIG.workspace.executable_projects.keys():
    app.command(name=prj_name, help=f"Run {prj_name}.")(create_build_command(prj_name))
