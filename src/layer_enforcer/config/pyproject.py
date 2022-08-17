import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Protocol, TypedDict

if sys.version_info >= (3, 11):  # pragma: nocover
    import tomllib
else:  # pragma: nocover
    import tomli as tomllib

from ..interfaces import LayersLoader
from .interfaces import Config, ConfigLoader
from .layers import LAYERS_PATH

CONFIG_PATH = Path("pyproject.toml")


@dataclass
class PyprojectConfig:
    modules: List[str] = field(default_factory=list)
    ignore: List[str] = field(default_factory=list)
    layers: str = ""


class LayerEnforcerDict(TypedDict):
    ignore: List[str]
    modules: List[str]
    layers: str


class LoadPyproject(Protocol):
    def __call__(self, path: Path) -> PyprojectConfig:
        """Parse pyproject.toml at ``path`` into :class:`PyprojectConfig`.

        Args:
            path: pyproject.toml file location.

        Returns:
            Parsed pyproject.toml settings data structure.
        """


def load_pyproject(path: Path) -> PyprojectConfig:
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return PyprojectConfig()

    try:
        config: LayerEnforcerDict = raw["tool"]["layer_enforcer"]
    except KeyError:
        return PyprojectConfig()

    return PyprojectConfig(
        modules=config.get("modules", []),
        ignore=config.get("ignore", []),
        layers=config.get("layers", LAYERS_PATH),
    )


class PyprojectTomlConfigLoader(ConfigLoader):
    path: Path
    parsed: Optional[PyprojectConfig]
    layers_loader: LayersLoader
    load_pyproject: LoadPyproject

    def __init__(
        self,
        path: Path,
        *,
        layers_loader: LayersLoader,
        load_pyproject: LoadPyproject = load_pyproject,
    ) -> None:
        self.path = path
        self.layers_loader = layers_loader
        self.parsed = None
        self.load_pyproject = load_pyproject

    def load(self, config: Config) -> Config:
        if self.parsed is None:
            self.parsed = pyproject = self.load_pyproject(self.path)
        else:
            pyproject = self.parsed

        if pyproject.modules:
            config.modules = set(pyproject.modules)

        if pyproject.ignore:
            config.ignore = set(pyproject.ignore)

        if pyproject.layers:
            config.layers = self.layers_loader.path(pyproject.layers)

        return config
