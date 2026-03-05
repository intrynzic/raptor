import tomllib

from packaging.version import parse as parse_ver

from raptor.config.defines import CONFIG_FILE_NAME, CONFIG_FILE_VERSION
from raptor.config.structs import RaptorConfig, RaptorConfigFile
from raptor.core.git import repo_root
from raptor.core.log import critical, warn


def load_config() -> RaptorConfig:
    cfg_path = repo_root() / CONFIG_FILE_NAME
    if not cfg_path.exists():
        critical(f"{CONFIG_FILE_NAME} is missing!")
        raise ValueError()

    with open(cfg_path, "rb") as f:
        data = tomllib.load(f)

    parsed = RaptorConfigFile.model_validate(data)
    res = parsed.raptor

    if parse_ver(res.version) != CONFIG_FILE_VERSION:
        warn(f"{CONFIG_FILE_NAME} file version v{res.version} does not match the installed version v{CONFIG_FILE_VERSION}!")
        warn("Certain configurations may be applied incorrectly.")

    return parsed.raptor

# Globally-accessible config settings
CONFIG: RaptorConfig = load_config()

# Debug prints all configuration settings to check if they loaded properly
def _debug_print_config():
    from raptor.core.log import trace

    trace("raptor")
    trace(f"    version: {CONFIG.version}")

    trace("raptor.paths")
    trace(f"    docs_dir: {CONFIG.paths.docs_dir}")
    trace(f"    temp_dir: {CONFIG.paths.temp_dir}")
    trace(f"    tools_dir: {CONFIG.paths.tools_dir}")

    trace("raptor.setup")
    trace(f"    headless: {CONFIG.setup.headless}")

    trace("raptor.setup.environment")
    for task in CONFIG.setup.environment:
        trace(f"    name = {task.name}; min_version = {task.min_version}")

    trace("raptor.doctor")
    for check in CONFIG.doctor.checks:
        trace(f"    {check.name}")

    trace("raptor.premake")
    trace(f"    default_action: {CONFIG.premake.default_action}")
    trace(f"    supported_actions: {CONFIG.premake.supported_actions}")

    trace("raptor.workspace")
    trace(f"    dir: {CONFIG.workspace.dir}")
    trace(f"    name: {CONFIG.workspace.name}")
    trace(f"    configs: {CONFIG.workspace.configs}")
    trace(f"    default_config: {CONFIG.workspace.default_config}")
    trace(f"    default_arch: {CONFIG.workspace.default_arch}")
    trace(f"    executable_projects: {CONFIG.workspace.executable_projects}")

    trace("raptor.clean")
    trace(f"    targets: {CONFIG.clean.targets}")

# Disabled by default
# _debug_print_config()
