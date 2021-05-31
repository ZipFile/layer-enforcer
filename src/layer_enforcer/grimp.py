from typing import Iterator, Set, Tuple

from grimp import build_graph
from grimp.application.ports.graph import AbstractImportGraph

from networkx.exception import NodeNotFound

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

    def find_import_chain(self, importer: str, imported: str) -> Tuple[str, ...]:
        try:
            chain = self.graph.find_shortest_chain(importer, imported)
        except NodeNotFound:
            chain = None

        if chain is not None:
            return chain

        return ()

    def find_imported_modules(self, module: str) -> Set[str]:
        return self.graph.find_upstream_modules(module)


def new_grimp_tree(*modules: str) -> Tree:
    graph = build_graph(*modules, include_external_packages=True)

    return GrimpTree(modules, graph)
