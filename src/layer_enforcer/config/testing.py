from pathlib import Path
from typing import Dict, Optional, Set, TextIO, Union

from ..interfaces import Layer, LayersLoader
from .interfaces import Config, ConfigLoader


class NoopConfigLoader(ConfigLoader):
    def load(self, config: Config) -> Config:
        return config


class StaticConfigLoader(ConfigLoader):
    def __init__(self, config: Config) -> None:
        self.config = config

    def load(self, config: Config) -> Config:
        return self.config


class StaticLayersLoader(LayersLoader):
    def __init__(
        self,
        text_io: Optional[Set[Layer]] = None,
        path: Optional[Dict[Union[Path, str], Set[Layer]]] = None,
    ) -> None:
        self._text_io = text_io or set()
        self._path = path or {}

    def text_io(self, f: TextIO) -> Set[Layer]:
        return self._text_io

    def path(self, path: Union[Path, str]) -> Set[Layer]:
        return self._path.get(path) or set()
