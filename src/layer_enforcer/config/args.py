from argparse import ArgumentParser, FileType
from dataclasses import dataclass
from typing import List, Optional, Protocol, Set, TextIO

from ..interfaces import LayersLoader
from .interfaces import Config, ConfigLoader
from .layers import LAYERS_PATH


@dataclass
class Args:
    modules: List[str]
    layers: TextIO
    ignore: Set[str]


class ParseArgs(Protocol):
    def __call__(self, argv: List[str]) -> Args:
        """Parse list of command line arguments into :class:`Args`.

        Args:
            argv: The list of command line arguments passed to a Python script. E.g. value of ``sys.argv[1:]``.

        Returns:
            Parsed args data structure.
        """


def parse_args(argv: List[str]) -> Args:
    parser = ArgumentParser()

    parser.add_argument("modules", nargs="+")
    parser.add_argument(
        "--layers",
        type=FileType("rt", encoding="utf-8"),
        default=LAYERS_PATH,
    )
    parser.add_argument(
        "--ignore",
        default=frozenset(),
        type=lambda s: set(s.split(",")),
    )

    args = parser.parse_args(argv)

    return Args(args.modules, args.layers, args.ignore)


class ArgparseConfigLoader(ConfigLoader):
    argv: List[str]
    parsed: Optional[Args]
    layers_loader: LayersLoader
    parse_args: ParseArgs

    def __init__(
        self,
        argv: List[str],
        *,
        layers_loader: LayersLoader,
        parse_args: ParseArgs = parse_args,
    ) -> None:
        self.argv = argv
        self.parsed = None
        self.layers_loader = layers_loader
        self.parse_args = parse_args

    def load(self, config: Config) -> Config:
        if self.parsed is None:
            self.parsed = args = self.parse_args(self.argv)
        else:
            args = self.parsed

        if args.modules:
            config.modules = set(args.modules)

        config.layers = self.layers_loader.text_io(args.layers)

        if args.ignore:
            config.ignore = args.ignore

        return config
