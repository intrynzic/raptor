import os
import time
from pathlib import Path
from typing import Optional, Sequence

from raptor.build.metabuild_backend import MetaBuildBackend, ToolRequirement
from raptor.config.loader import CONFIG
from raptor.core.fs import repo_root
from raptor.core.log import info, trace
from raptor.core.process import run


class Premake(MetaBuildBackend):
    name = "premake"
    friendly_name = "Premake"

    @property
    def tool_requirements(self) -> Sequence[ToolRequirement]:
        return [ToolRequirement(name="premake", min_ver=CONFIG.metabuild.min_version, auto_install=True)]

    def generate(self, args: Optional[list[str]]):
        self._premake(args if args else [])

    def detect(self) -> bool:
        return super().detect()

    @staticmethod
    def _premake(args: list[str]):
        run([_premake_path()] + args, cwd=repo_root())
        if args[0].lower() == "vs2026":
            Premake._post_process_vs2026()

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
    @staticmethod
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


# TODO: This function must be FULLLY REWORKED
# We will now no-longer be shipping premake with Raptor (it's dumb... Very)
def _premake_path() -> Path:
    return Path()


# @cache
# def _premake_path() -> Path:
#     binary = "premake5.exe" if platform.system() == "Windows" else "premake5"
#     path = Path(str(files("raptor").joinpath(f"bin/{binary}")))
#
#     if not path.exists():
#         critical(f'Premake5 binary not found at "{path}"!')
#         return Path()
#
#     return path
