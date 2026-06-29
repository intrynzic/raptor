from collections.abc import Callable
from pathlib import Path

import typer

from raptor.config.loader import CONFIG
from raptor.config.structs import Task
from raptor.core.git import repo_root
from raptor.core.log import error
from raptor.core.msbuild import build, build_and_run, run_project
from raptor.core.process import run

app = typer.Typer(help="Build and run an executable project or run raptor tasks.")


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


# Maps task names to their generated command handlers.
#
# This registry serves two purposes:
#   - Allows task dependencies to invoke other tasks by name.
#   - Prevents command-generation logic from needing to repeatedly search
#     for registered tasks.
#
# Entries are populated during startup when tasks are loaded from the configuration file.
_task_run_commands: dict[str, Callable[[], None]] = {}


# Factory function for creating task-run commands
def create_taskrun_command(task_name: str, task: Task):
    """
    Creates a Typer command handler for a configured task.

    The generated command executes all dependent tasks first, in the order
    they are declared, before executing the task's own command if present.

    Once created, the command is registered in the local task registry so
    that other tasks may invoke it through dependency resolution.

    Parameters
    ----------
    task_name:
        Unique name of the task as defined in the configuration file.

    task:
        Task configuration describing the command, arguments, working
        directory, and task dependencies.

    Returns
    -------
    Callable
        A zero-argument command handler suitable for registration with
        Typer.
    """

    def command():
        # Execute all dependent tasks before running this task
        if task.depends_on:
            for dependency in task.depends_on:
                _task_run_commands[dependency]()
                print()

        # Execute this task's command
        if task.command:
            cwd = (repo_root() / task.cwd) if task.cwd else repo_root()
            run([task.command] + task.args, cwd=cwd)

    _task_run_commands[task_name] = command
    return command


# Generate and register a Typer command for every configured task.
# Each task becomes directly invokable from the command line using its configured name.
for task_name, task in CONFIG.tasks.items():
    app.command(name=task_name, help=task.description)(create_taskrun_command(task_name, task))
