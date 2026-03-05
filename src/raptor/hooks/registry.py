from typing import Callable, Dict

HOOK_REGISTRY: Dict[str, Callable] = {}


def register_hook(name: str):
    def decorator(func: Callable):
        HOOK_REGISTRY[name] = func
        return func

    return decorator
