import os
import time

import typer

from raptor.config.loader import CONFIG
from raptor.core.fs import premake_path
from raptor.core.git import repo_root
from raptor.core.log import info, trace
from raptor.core.process import run

app = typer.Typer(help = "Generate project files using premake.")

@app.command(help = f"Alias for {CONFIG.premake.default_action}.")
def default():
    match CONFIG.premake.default_action:
        case "vs2026":
            vs2026()
        case "vs2022":
            vs2022()

if "vs2026" in CONFIG.premake.supported_actions:
    @app.command(help = "Generate project files for Visual Studio 2026.")
    def vs2026():
        info("Generating Visual Studio 2026 project files...")
        _premake("vs2026")
        print()
        _post_process()

if "vs2022" in CONFIG.premake.supported_actions:
    @app.command(help = "Generate project files for Visual Studio 2022.")
    def vs2022():
        info("Generating Visual Studio 2022 project files...")
        _premake("vs2022")

def _premake(action: str):
    run([premake_path(), action], cwd = repo_root())

# NOTE: The new Visual Studio 2026 .slnx format is much stricter regarding platform configurations than 2022 was.
# Despite 'platforms' listing only 'x64' in 'premake5.lua', C# projects now default to the 'AnyCPU' platform/architecture.
#
# Using some Premake hacks, we work around this issue, but stumble right into another one: the conditions on
# property groups now get incorrectly outputted as:
# '<PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug X64|AnyCPU' ">'
#
# To fix this, post-processing is performed on all .csproj files to replace 'Debug x64|AnyCPU' with `Debug|AnyCPU`
# - as it's supposed to be.
#
# This fix only addresses the symptoms, but not the root cause - which is a mismatch in how Premake handles platforms
# in MSBuild vs MSVC. Hopefully this will be fixed soon.
def _post_process():
    start = time.perf_counter()
    info("Post-processing Visual Studio 2026 project files...")

    # Recursively finds all .csproj files and applies the required fix
    def _fix_csproj(path: str):
        with open(path, "r", encoding = "utf-8") as f:
            content = f.read()

        new_content = content.replace(" x64|", "|")
        if new_content != content:
            with open(path, "w", encoding = "utf-8") as f:
                f.write(new_content)

            trace(f"Fixed {path.replace("\\", "/")[2:]}...")

    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".csproj"):
                _fix_csproj(os.path.join(root, file))

    end = time.perf_counter()
    elapsedMs = (end - start) * 1000
    info(f"Done ({elapsedMs:.0f}ms).")
