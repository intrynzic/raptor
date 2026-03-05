from raptor.core.log import info, warn, error, critical, _log
from raptor.core.validation import Severity
from raptor.doctor.checks.check import Check
from raptor.doctor.registry import get_checks, type_id_to_check
import json
import os
import typer


_DOCTOR_FILE = ".raptordoctor"

app = typer.Typer(help = "Diagnose and fix issues with the repository and your development environment.")

@app.command(help = "Perform a full diagnostic check and create report.")
def diagnose():
    checks = get_checks()

    info("Raptor Doctor Diagnostics")
    info("============================")

    with open(_DOCTOR_FILE, 'w') as f:
        info(f"Running diagnostics on {len(checks)} checks...")
        passed = 0
        failed = 0
        for check in checks:
            result = check.validate()
            check.last_result = result

            f.write(json.dumps(check.to_dict()) + '\n')

            if result.valid:
                _ok(check)
                passed += 1
                continue

            failed += 1
            match result.severity:
                case Severity.WARNING:
                    _warn(check)
                case Severity.ERROR:
                    _fail(check)
                case Severity.CRITICAL:
                    _critical(check)

            if result.message:
                _message(result.message)

    info(f"Passed: {passed}, Failed: {failed}.")

@app.command(help = "Attempt to auto-fix all checks that failed during diagnostics.")
def fix(
    no_auto_delete: bool = typer.Option(False, "--no-auto-delete", help = f"Disable auto-deleting the {_DOCTOR_FILE} file after running.")
):
    def auto_delete():
        if not no_auto_delete:
            os.remove(_DOCTOR_FILE)

    if not os.path.exists(_DOCTOR_FILE):
        critical(f"The {_DOCTOR_FILE} log file does not exist! Please run \"raptor doctor diagnose\" first.")
        return

    must_fix: list[Check] = []
    with open(_DOCTOR_FILE, 'r') as f:
        for line in f.readlines():
            data: dict = json.loads(line)
            check = type_id_to_check(data["type_id"])
            if check is None:
                error(f"Failed to read check '{data["type_id"]}' from {_DOCTOR_FILE}!")
                break

            check.from_dict(data)
            if check.last_result is not None and not check.last_result.valid:
                must_fix.append(check)

    if not must_fix:
        info("There is nothing to fix.")
        auto_delete()
        return

    info(f"Attempting fixes on {len(must_fix)} check(s)...")

    fixed = 0
    failed = 0
    skipped = 0
    for check in must_fix:
        if check.can_fix:
            info(f"Fixing: {check.name}...")
            if check.fix():
                # Validate after fix
                result = check.validate()
                if result.valid:
                    _ok(check)
                    fixed += 1
                    continue

                failed += 1
                match result.severity:
                    case Severity.WARNING:
                        _warn(check)
                    case Severity.ERROR:
                        _fail(check)
                    case Severity.CRITICAL:
                        _critical(check)

                if result.message:
                    _message(result.message)
        else:
            warn(f"Cannot auto-fix '{check.name}'!")
            skipped += 1

    info(f"Fixed: {fixed}, Failed: {failed}, Skipped: {skipped}.")
    auto_delete()

def _ok(check: Check):
    _log("[OK]:", check.name, fg = typer.colors.BRIGHT_GREEN)

def _warn(check: Check):
    _log("[WARN]:", check.name, fg = typer.colors.YELLOW)

def _fail(check: Check):
    _log("[FAIL]:", check.name, fg = typer.colors.RED, err = True)

def _critical(check: Check):
    _log("[CRITICAL]:", check.name, fg = typer.colors.BRIGHT_WHITE, bg = typer.colors.RED, err = True)

def _message(msg: str):
    _log("  └─ ", msg, fg = typer.colors.YELLOW)
