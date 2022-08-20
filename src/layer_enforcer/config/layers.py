from collections.abc import Mapping
from pathlib import Path
from typing import Iterator, List, Optional, Protocol, Set, TextIO, TypedDict, Union

from yaml import YAMLError, safe_load

from ..interfaces import InvalidLayerFormat, Layer, LayersLoader

LAYERS_PATH = "layers.yml"


class LayerDict(TypedDict):
    name: str
    submodules: List[str]
    imports: List[str]
    # https://github.com/python/mypy/issues/731
    layers: List["LayerDict"]  # type:ignore[misc]


class DictToLayers(Protocol):
    def __call__(
        self,
        raw_layer: LayerDict,
        parent: Optional[Layer] = None,
    ) -> Iterator[Layer]:
        """Convert primitive ``dict`` to ``Layer``s."""


def _dict_to_layers(
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
        yield from _dict_to_layers(raw_layer, parent)


class NotAYamlError(InvalidLayerFormat):
    """Provided file is not a YAML."""


class NotADictError(InvalidLayerFormat):
    """Root element of the YAML document must be a dict."""


class YamlLayersLoader(LayersLoader):
    dict_to_layers: DictToLayers

    def __init__(self, dict_to_layers: DictToLayers = _dict_to_layers):
        self.dict_to_layers = dict_to_layers

    def text_io(self, f: TextIO) -> Set[Layer]:
        try:
            parsed_yaml: LayerDict = safe_load(f)
        except YAMLError as e:
            raise NotAYamlError("Layers specification is not a valid YAML file.") from e

        if not isinstance(parsed_yaml, Mapping):
            raise NotADictError(
                "Provided layer specification must be a dict at the root of the "
                "YAML document."
            )

        return set(self.dict_to_layers(parsed_yaml))

    def path(self, path: Union[Path, str]) -> Set[Layer]:
        if isinstance(path, str):
            f = open(path, "rt", encoding="utf-8")
        else:
            f = path.open("rt", encoding="utf-8")

        with f:
            return self.text_io(f)
