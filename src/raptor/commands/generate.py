import secrets
import webbrowser

import typer

from raptor.core.fs import docs_dir, doxygen_dir
from raptor.core.git import repo_root
from raptor.core.log import critical, info
from raptor.core.process import run

app = typer.Typer(help = "Generate various Intricate-specific resources, documentation and identifiers.")

@app.command(help = "Generate IntricateEngine GUIDs.", no_args_is_help = True)
def guid(
    count: int = typer.Option(1, "--count", "-c", help = "The number of GUIDs to generate."),
    builtin: bool = typer.Option(False, "--builtin", "-b", help = "Generate GUIDs following Intricate's pattern for built-in GUIDs."),
    length: int = typer.Option(32, "--length", "-l", help = "The character-length of the GUIDs to generate.")
):
    _IE_BUILTIN_ASSET_GUID_PREFIX: str = "b0000000"
    _IE_BUILTIN_ASSET_GUID_PREFIX_LENGTH: int = len(_IE_BUILTIN_ASSET_GUID_PREFIX)

    # INVARIANT: Cannot generate zero or less GUIDs
    if count <= 0:
        critical(f"Cannot generate {count} GUIDs!")
        return

    # INVARIANT: GUID length must be greater than _IE_BUILTIN_ASSET_GUID_PREFIX_LENGTH
    if builtin:
        if (length <= _IE_BUILTIN_ASSET_GUID_PREFIX_LENGTH):
            critical("The length of the GUID cannot be less than the built-in GUID prefix length when generating built-in GUIDs!")
            return

    # INVARIANT: Length must be a positive non-zero integer
    if length <= 0:
        critical("The length of the GUID must be a positive non-zero integer!")
        return

    generated: list[str] = []
    for _ in range(count):
        my_length = (length - _IE_BUILTIN_ASSET_GUID_PREFIX_LENGTH) if builtin else length
        num_bytes = (my_length + 1) // 2
        generated.append(f"{_IE_BUILTIN_ASSET_GUID_PREFIX if builtin else ""}{secrets.token_hex(num_bytes)[:my_length]}")

    info(f"Generated GUIDs:\n{'\n'.join(generated)}")

@app.command(help = "Generate project documentation with Doxygen.")
def docs(open_browser: bool = typer.Option(False, "--open", "-o", help = "Open the generated documentation in the browser.")):
    root = repo_root()
    doxygen = doxygen_dir() / "doxygen.exe"

    if not doxygen.exists():
        critical("doxygen.exe could not be found!\n Please run \"raptor setup doxygen\" to install Doxygen.")
        return

    info("Running Doxygen...")
    run([doxygen, "doxyfile"], cwd = root)

    index_path = docs_dir() / "html" / "index.html"
    if not (index_path):
        critical("Doxygen generation failed!")
        return

    if open_browser:
        webbrowser.open(f"file://{index_path}")
