import importlib.util

from raptor.core.fs import hooks_dir
from raptor.core.log import error


def load_hooks():
    if not hooks_dir().exists():
        return

    for hook_path in sorted(hooks_dir().glob("*.py")):
        spec = importlib.util.spec_from_file_location(f"raptor_user_hook_{hook_path.name}", hook_path)
        if spec is None:
            error(f"Failed to load hook '{hook_path}'!")
            return

        module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)
