from raptor.core.validation import ValidationResult, Severity
import sys
import typer
import typer.colors
from datetime import datetime


def trace(msg: str):
    _log("[TRACE]:", msg, fg = typer.colors.BRIGHT_BLACK)

def info(msg: str):
    _log("[INFO]:", msg, fg = typer.colors.CYAN)

def command(cmd: str):
    _log(">", cmd, fg = typer.colors.BRIGHT_CYAN)

def warn(msg: str):
    _log("[WARN]:", msg, fg = typer.colors.YELLOW)

def error(msg: str, e: Exception | None = None):
    _log("[ERROR]:", f"{msg}{'\n' + str(e) if e else ''}", fg = typer.colors.RED, err = True)

def critical(msg: str, e: Exception | None = None):
    _log("[CRITICAL]:", f"{msg}{'\n' + str(e) if e else ''}", fg = typer.colors.BRIGHT_WHITE, bg = typer.colors.RED, err = True)
    typer.Exit(1)
    sys.exit(1)

def log_validation_result(vres: ValidationResult):
    if vres.message is None:
        return

    match vres.severity:
        case Severity.NONE:
            info(vres.message)
        case Severity.WARNING:
            warn(vres.message)
        case Severity.ERROR:
            error(vres.message)
        case Severity.CRITICAL:
            critical(vres.message)
        case _:
            trace(vres.message)

def _log(prefix: str, message: str, fg: int | str | None = None, bg: int | str | None = None, err: bool = False):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] {prefix} {message}"
    typer.secho(formatted, fg = fg, bg = bg, err = err)
