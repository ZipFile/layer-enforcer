import sys
from importlib import import_module
from types import ModuleType
from typing import Callable

from .config.args import ArgparseConfigLoader
from .config.interfaces import Config, ConfigLoader
from .config.layers import YamlLayersLoader
from .config.multiple import MultipleConfigLoader
from .config.pyproject import CONFIG_PATH, PyprojectTomlConfigLoader
from .impl import match_modules
from .interfaces import MatchModules
from .utils import load_factory

DEFAULT_LAYER_LOADER = YamlLayersLoader()
DEFAULT_CONFIG_LOADER = MultipleConfigLoader(
    [
        PyprojectTomlConfigLoader(
            CONFIG_PATH,
            layers_loader=DEFAULT_LAYER_LOADER,
        ),
        ArgparseConfigLoader(
            sys.argv[1:],
            layers_loader=DEFAULT_LAYER_LOADER,
        ),
    ],
)


def main(
    writeln: Callable[[str], None] = print,  # noqa: T202
    import_module: Callable[[str], ModuleType] = import_module,
    match_modules: MatchModules = match_modules,
    config_loader: ConfigLoader = DEFAULT_CONFIG_LOADER,
) -> None:
    config = config_loader.load(Config())

    if not config.modules:
        writeln("No modules to check.")
        sys.exit(10)

    tree_factory = load_factory(config.tree_factory_module, import_module)
    tree = tree_factory(*config.modules)
    conflicts = match_modules(tree=tree, layers=config.layers)
    has_conflicts = False

    for conflict in conflicts:
        if conflict.main.module in config.ignore:
            continue

        has_conflicts = True
        writeln(f"{conflict.main.module}:")
        writeln(f"  Main layer: {conflict.main.layer.name}")

        for chain in conflict.main.chains:
            writeln(f"    {' -> '.join(chain)}")

        writeln(f"  Conflicts with: {conflict.dupe.layer.name}")

        for chain in conflict.dupe.chains:
            writeln(f"    {' -> '.join(chain)}")

        writeln("")

    if has_conflicts:
        sys.exit(9)
