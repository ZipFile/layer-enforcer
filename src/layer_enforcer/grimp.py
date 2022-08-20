from typing import Iterator, Set, Tuple

from grimp import build_graph
from grimp.application.ports.graph import AbstractImportGraph
from grimp.exceptions import ModuleNotPresent
from networkx.exception import NodeNotFound  # type: ignore[import]

from .interfaces import Tree


class GrimpTree(Tree):
    graph: AbstractImportGraph
    modules: Tuple[str, ...]

    def __init__(self, modules: Tuple[str, ...], graph: AbstractImportGraph) -> None:
        self.graph = graph
        self.modules = modules

    def walk(self) -> Iterator[str]:
        for module in self.modules:
            yield module
            yield from self.graph.find_descendants(module)

    def find_chains(self, importer: str, imported: str) -> Iterator[Tuple[str, ...]]:
        try:
            yield from self.graph.find_all_simple_chains(importer, imported)
        except ModuleNotPresent:
            pass

    def find_upstream_modules(self, module: str) -> Set[str]:
        try:
            return self.graph.find_upstream_modules(module)
        except NodeNotFound:
            return set()


def new_grimp_tree(*modules: str) -> Tree:
    graph = build_graph(*modules, include_external_packages=True)

    return GrimpTree(modules, graph)
