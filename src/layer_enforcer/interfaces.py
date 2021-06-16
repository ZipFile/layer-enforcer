from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import AbstractSet, Iterable, Iterator, List, Optional, Protocol, Set, Tuple

EMPTY_SET: AbstractSet[str] = frozenset()


@dataclass(frozen=True)
class Layer:
    name: str
    parent: Optional["Layer"] = field(compare=False, default=None)
    imports: AbstractSet[str] = field(compare=False, default=EMPTY_SET)
    submodules: AbstractSet[str] = field(compare=False, default=EMPTY_SET)

    def __repr__(self) -> str:
        return repr(self.name)


@dataclass
class Match:
    module: str
    layer: Layer
    chains: List[Tuple[str, ...]] = field(default_factory=list)
    submodules: Set[str] = field(default_factory=set)

    def __bool__(self) -> bool:
        return bool(self.chains or self.submodules)


@dataclass
class Conflict:
    main: Match
    dupe: Match


class Tree(metaclass=ABCMeta):
    @abstractmethod
    def walk(self) -> Iterator[str]:
        """Iterate over all sumbodules."""

    @abstractmethod
    def find_chains(self, importer: str, imported: str) -> Iterator[Tuple[str, ...]]:
        """Return import chains from ``importer`` to ``import``."""

    @abstractmethod
    def find_downstream_modules(self, module: str) -> Set[str]:
        """Find all modules directly or indirectly imported by ``module``."""


class TreeFactory(Protocol):
    def __call__(self, *modules: str) -> Tree:
        """Make tree walker for given modules."""


class MatchModules(Protocol):
    def __call__(self, tree: Tree, layers: Set[Layer]) -> Iterable[Conflict]:
        """Find conflicts within import tree."""
