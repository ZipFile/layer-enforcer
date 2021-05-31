from functools import lru_cache
from typing import Dict, Iterable, Set

from .interfaces import Conflict, Layer, Match, Tree
from .utils import depth, is_import_allowed, match_submodule

INF = float("+inf")


def match_modules(tree: Tree, layers: Set[Layer]) -> Iterable[Conflict]:
    module_matches: Dict[str, Match] = {}
    modules: Set[str] = set()

    for module in tree.walk():
        modules.add(module)

        for layer in layers:
            match = Match(module, layer)

            for import_ in layer.imports:
                chain = tree.find_import_chain(module, import_)

                if chain:
                    match.chains.append(chain)

            for submodule in layer.submodules:
                if match_submodule(module, submodule):
                    match.submodules.add(submodule)

            if match:
                try:
                    yield Conflict(module_matches[module], match)
                except KeyError:
                    module_matches[module] = match

    @lru_cache(None)
    def key(module: str) -> float:
        try:
            return depth(module_matches[module].layer)
        except KeyError:
            return INF

    for module in sorted(modules, key=key):
        current_match = module_matches.get(module)

        for imported in sorted(tree.find_imported_modules(module), key=key):
            try:
                imported_match = module_matches[imported]
            except KeyError:
                continue

            if current_match is None:
                chain = tree.find_import_chain(module, imported)

                if chain:
                    module_matches[module] = current_match = Match(
                        module,
                        imported_match.layer,
                        chains=[chain],
                    )
                else:
                    continue

            if is_import_allowed(current_match.layer, imported_match.layer):
                continue

            yield Conflict(current_match, imported_match)
