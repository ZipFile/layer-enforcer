import sys
from argparse import ArgumentParser, FileType
from dataclasses import dataclass, field
from importlib import import_module
from types import ModuleType
from typing import Callable, Iterator, List, Optional, Set, TextIO, TypedDict

from yaml import safe_load

from .impl import match_modules
from .interfaces import Layer, MatchModules
from .utils import load_factory


@dataclass
class Args:
    modules: List[str]
    layers: TextIO
    ignore: Set[str] = field(default_factory=set)
    tree_factory_module: str = "layer_enforcer.grimp:new_grimp_tree"


def parse_args(argv: List[str]) -> Args:
    parser = ArgumentParser()

    parser.add_argument("modules", nargs="+")
    parser.add_argument(
        "--layers",
        type=FileType("rt", encoding="utf-8"),
        default="layers.yml",
    )
    parser.add_argument(
        "--ignore",
        default=frozenset(),
        type=lambda s: set(s.split(",")),
    )

    args = parser.parse_args(argv)

    return Args(args.modules, args.layers, args.ignore)


class LayerDict(TypedDict):
    name: str
    submodules: List[str]
    imports: List[str]
    layers: List["LayerDict"]


def dict_to_layers(
    raw_layer: LayerDict,
    parent: Optional[Layer] = None,
) -> Iterator[Layer]:
    parent = Layer(
        name=raw_layer["name"],
        parent=parent,
        imports=frozenset(raw_layer.get("imports", [])),
        submodules=frozenset(raw_layer.get("submodules", [])),
    )

    yield parent

    for raw_layer in raw_layer.get("layers", []):
        yield from dict_to_layers(raw_layer, parent)


def parse_layers(layers: TextIO) -> Set[Layer]:
    parsed_yaml: LayerDict = safe_load(layers)

    return set(dict_to_layers(parsed_yaml))


def main(
    argv: List[str] = sys.argv,
    writeln: Callable[[str], None] = print,
    import_module: Callable[[str], ModuleType] = import_module,
    match_modules: MatchModules = match_modules,
) -> None:
    args = parse_args(argv[1:])
    tree_factory = load_factory(args.tree_factory_module, import_module)
    tree = tree_factory(*args.modules)
    layers = parse_layers(args.layers)
    conflicts = match_modules(tree=tree, layers=layers)
    has_conflicts = False

    for conflict in conflicts:
        if conflict.main.module in args.ignore:
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
