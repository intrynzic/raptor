import os
import time

import typer

from raptor.config.loader import CONFIG
from raptor.core.fs import premake_path
from raptor.core.git import repo_root
from raptor.core.log import info, trace
from raptor.core.process import run

from pathlib import Path

app = typer.Typer(help="Generate project files using premake.")


@app.command(help=f"Alias for {CONFIG.premake.default_action}.")
def default():
    match CONFIG.premake.default_action:
        case "vs2026":
            vs2026()
        case "vs2022":
            vs2022()


if "vs2026" in CONFIG.premake.supported_actions:

    @app.command(help="Generate project files for Visual Studio 2026.")
    def vs2026():
        info("Generating Visual Studio 2026 project files...")
        _premake("vs2026")
        print()
        _post_process_vs2026()


if "vs2022" in CONFIG.premake.supported_actions:

    @app.command(help="Generate project files for Visual Studio 2022.")
    def vs2022():
        info("Generating Visual Studio 2022 project files...")
        _premake("vs2022")


def _premake(action: str):
    run([premake_path(), action], cwd=repo_root(), quiet = True)


# NOTE: The Visual Studio 2026 .slnx format is significantly stricter about platform
# configuration consistency than previous Visual Studio releases.
#
# Even when only 'x64' is specified in the workspace configuration, C# projects still
# default to the 'AnyCPU' platform. Premake currently generates incorrect MSBuild
# property group conditions in this scenario:
#
#   <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug x64|AnyCPU' ">
#
# The expected condition is:
#
#   <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
#
# To work around this Premake/MSBuild platform mismatch, all generated .csproj files
# are post-processed and occurrences of:
#
#   "<Configuration> x64|"
#
# are replaced with:
#
#   "<Configuration>|"
#
# This addresses the generated project file incompatibility required by Visual Studio
# 2026, but does not resolve the underlying issue in Premake's C# project generation.
def _post_process_vs2026():
    start = time.perf_counter()
    info("Post-processing Visual Studio 2026 project files...")

    # Recursively finds all .csproj files and applies the required fix
    def _fix_csproj(path: Path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content.replace(" x64|", "|")
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)

            trace(f"Fixed {path.relative_to(repo_root()).as_posix()}...")

    for root, dirs, files in os.walk(repo_root()):
        for file in files:
            if file.endswith(".csproj"):
                _fix_csproj(Path(root) / file)

    end = time.perf_counter()
    elapsedMs = (end - start) * 1000
    info(f"Done ({elapsedMs:.0f}ms).")
