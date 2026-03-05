from raptor.config.loader import CONFIG
from raptor.core.fs import msbuild_path
from raptor.core.git import repo_root
from raptor.core.log import critical
from raptor.core.process import run
from pathlib import Path
from typing import Literal


_BuildTargets = Literal["Build", "Rebuild", "Clean"]

def build(config: str, arch: str):
    _msbuild_solution("Build", config, arch)

def rebuild(config: str, arch: str):
    _msbuild_solution("Rebuild", config, arch)

def clean(config: str, arch: str):
    _msbuild_solution("Clean", config, arch)

def build_and_run(prj_path: Path, config: str, arch: str, args: list[str] | None = None):
    _msbuild_project(prj_path, "Build", config, arch)
    run_project(prj_path, config, arch, args)

def run_project(prj_path: Path, config: str, arch: str, args: list[str] | None = None):
    out_path = _msbuild_get_project_target_path(prj_path, config, arch).with_suffix(".exe")
    if out_path.exists():
        run([out_path] + (args if args is not None else []), cwd = out_path.parent)

def _msbuild_solution(target: _BuildTargets, config: str, arch: str):
    root = repo_root()
    msbuild = msbuild_path()

    sln_path_stem = root / CONFIG.workspace.dir / CONFIG.workspace.name
    new_sln = sln_path_stem.with_suffix(".slnx")
    old_sln = sln_path_stem.with_suffix(".sln")
    sln = new_sln if new_sln.exists() else old_sln

    if not sln.exists():
        critical(f"Neither '{new_sln.name}' nor '{old_sln.name}' could not be found! Please run \"raptor premake default\".")
        return

    run([msbuild, sln, "/restore", "/m", f"/t:{target}", f"/p:Configuration={config}", f"/p:Platform={arch}",
         "/p:UseSharedCompilation=true"], cwd = root)

def _msbuild_project(prj_path: Path, target: _BuildTargets, config: str, arch: str):
    root = repo_root()
    msbuild = msbuild_path()
    prj = root / prj_path

    if not prj.exists():
        critical(f"{prj.name} could not be found! Please run \"raptor premake default\".")
        return

    run([msbuild, prj, "/restore", "/m", f"/t:{target}", f"/p:Configuration={config}",
         f"/p:Platform={arch}", "/p:UseSharedCompilation=true", f"/p:SolutionDir={str(root)}\\"], cwd = root)

def _msbuild_get_project_target_path(prj_path: Path, config: str, arch: str) -> Path:
    root = repo_root()
    msbuild = msbuild_path()
    prj = root / prj_path

    if not prj.exists():
        critical(f"{prj.name} could not be found! Please run \"raptor premake default\".")
        return Path()

    return Path(run([msbuild, prj, f"/p:Configuration={config}", f"/p:Platform={arch}", "/getProperty:TargetPath"],
                        cwd = root, capture = True))
