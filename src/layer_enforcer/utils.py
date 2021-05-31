from importlib import import_module
from types import ModuleType
from typing import Callable, Iterator, Optional

from .interfaces import Layer, TreeFactory


def traverse_layers(layer: Optional[Layer]) -> Iterator[Layer]:
    while layer is not None:
        yield layer
        layer = layer.parent


def depth(layer: Layer) -> int:
    return sum(1 for layer in traverse_layers(layer))


def is_import_allowed(layer: Layer, target: Layer) -> bool:
    for layer in traverse_layers(layer):
        if layer is target:
            return True
    return False


def match_submodule(module: str, submodule: str) -> bool:
    return (
        module == submodule
        or f".{submodule}." in module
        or module.endswith(f".{submodule}")
        or module.startswith(f"{submodule}.")
    )


def load_factory(
    import_string: str,
    import_module: Callable[[str], ModuleType] = import_module,
) -> TreeFactory:
    name, attr = import_string.rsplit(":", 1)
    module = import_module(name)
    return getattr(module, attr)
