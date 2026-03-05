import os
import shutil
import time
from pathlib import Path

import typer

from raptor.config.loader import CONFIG
from raptor.config.structs import CleanTarget
from raptor.core.git import repo_root
from raptor.core.log import error, info, trace, warn

app = typer.Typer(help = "Clean the workspace's configured clean targets.")

@app.command(help = "Clean all targets.")
def all():
    start = time.perf_counter()
    for name, target in CONFIG.clean.targets.items():
        create_clean_command(name, target, False)()
        print()

    end = time.perf_counter()
    elapsedMs = (end - start) * 1000
    info(f"Done ({elapsedMs:.0f}ms).")

# Factory function for creating commands for each clean target
def create_clean_command(name: str, target: CleanTarget, print_time: bool):
    def command():
        if print_time:
            start = time.perf_counter()

        info(f"Cleaning {name}...")
        _clean_target(target)

        if print_time:
            end = time.perf_counter()
            elapsedMs = (end - start) * 1000
            info(f"Done ({elapsedMs:.0f}ms).")

    return command

for name, target in CONFIG.clean.targets.items():
    app.command(name = name, help = f"Clean the {name} target.")(create_clean_command(name, target, True))

def _clean_target(target: CleanTarget):
    # Handle delete_dirs first
    for dir in target.delete_dirs:
        abs_dir = repo_root() / dir
        if abs_dir.exists():
            _delete_folder(abs_dir)

    for dir in target.search_dirs:
        abs_dir = repo_root() / dir
        if not abs_dir.exists():
            warn(f"Directory \"{abs_dir}\" does not exist! Skipping...")
            continue

        if target.depth == "shallow":
            _shallow_delete_matching(abs_dir, target.files, target.file_exts)
        elif target.depth == "recursive":
            _recursive_delete_matching(abs_dir, target.files, target.file_exts)

def _delete_file(abs_path: Path):
    try:
        os.remove(abs_path)
        trace(f"Deleted file: \"{abs_path}\".")
    except Exception as e:
        error(f"Failed to delete file \"{abs_path}\"!", e)

def _delete_folder(abs_path: Path):
    try:
        shutil.rmtree(abs_path)
        trace(f"Deleted folder: \"{abs_path}\".")
    except Exception as e:
        error(f"Failed to delete folder: \"{abs_path}\"!", e)

def _shallow_delete_matching(root: Path, files: list[Path], file_exts: list[str]):
    try:
        for name in os.listdir(root):
            full_path = (root / name).resolve()

            # Delete matching files
            if full_path.is_file():
                rel_path = full_path.relative_to(repo_root())
                if any(name.endswith(ext) for ext in file_exts) or (full_path in files) or (rel_path in files):
                    _delete_file(full_path)
    except Exception as e:
        error(f"Failed to read directory \"{root}\"!", e)

def _recursive_delete_matching(root: Path, files: list[Path], file_exts: list[str]):
    for dir_path, dir_names, file_names in os.walk(root, topdown = False):
        dir_path = Path(dir_path)

        # Delete matching files
        for file_name in file_names:
            full_path = (dir_path / file_name).resolve()
            rel_path = full_path.relative_to(repo_root())

            if any(file_name.endswith(ext) for ext in file_exts) or (file_name in files) or (rel_path in files):
                _delete_file(full_path)
