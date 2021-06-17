from functools import lru_cache
from typing import Dict, Iterable, Set, Tuple

from .interfaces import Conflict, Layer, Match, Tree
from .utils import depth, is_import_allowed, match_submodule


def match_layer(tree: Tree, layer: Layer, module: str) -> Match:
    match = Match(module, layer)

    for import_ in layer.imports:
        match.chains.extend(tree.find_chains(module, import_))

    for submodule in layer.submodules:
        if match_submodule(module, submodule):
            match.submodules.add(submodule)

    return match


def match_modules(tree: Tree, layers: Set[Layer]) -> Iterable[Conflict]:
    module_matches: Dict[str, Match] = {}
    modules: Set[str] = set()
    ordered_layers = sorted(layers, key=lambda l: (depth(l), l.name))
    max_depth = 0

    for module in tree.walk():
        modules.add(module)

        for layer in ordered_layers:
            if match := match_layer(tree, layer, module):
                try:
                    yield Conflict(module_matches[module], match)
                except KeyError:
                    max_depth = max(max_depth, depth(layer))
                    module_matches[module] = match

    @lru_cache(None)
    def key(module: str) -> Tuple[int, str, str]:
        try:
            layer = module_matches[module].layer
        except KeyError:
            return max_depth + 1, "", module
        return depth(layer), layer.name, module

    for module in sorted(modules, key=key, reverse=True):
        current_match = module_matches.get(module)

        for imported in sorted(tree.find_upstream_modules(module), key=key):
            try:
                imported_match = module_matches[imported]
            except KeyError:
                continue

            if current_match is None:
                module_matches[module] = current_match = Match(
                    module=module,
                    layer=imported_match.layer,
                    chains=list(tree.find_chains(module, imported)),
                )
                continue

            if is_import_allowed(current_match.layer, imported_match.layer):
                continue

            yield Conflict(
                main=current_match,
                dupe=Match(
                    module=current_match.module,
                    layer=imported_match.layer,
                    chains=list(tree.find_chains(module, imported)),
                ),
            )
