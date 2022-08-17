from io import StringIO
from pathlib import Path
from typing import Iterator, Optional, Set, TextIO, Union

from pytest import fixture, mark, raises

from layer_enforcer.config.layers import (
    DictToLayers,
    LayerDict,
    NotADictError,
    NotAYamlError,
    YamlLayersLoader,
    _dict_to_layers,
)
from layer_enforcer.interfaces import Layer


class TestDictToLayers:
    def test_ok(self) -> None:
        layers = list(
            _dict_to_layers(
                {
                    "name": "level0",
                    "submodules": ["a", "b"],
                    "imports": ["i", "j"],
                    "layers": [
                        {
                            "name": "level1x",
                            "submodules": ["c", "d"],
                        },
                        {
                            "name": "level1y",
                            "layers": [
                                {
                                    "name": "level2",
                                    "imports": ["k", "l"],
                                },
                            ],
                        },
                    ],
                }
            )
        )

        expected_layers = [
            Layer(
                name="level0",
                parent=None,
                imports=frozenset(["i", "j"]),
                submodules=frozenset(["a", "b"]),
            ),
        ]
        expected_layers.extend(
            [
                Layer(
                    name="level1x",
                    parent=expected_layers[0],
                    submodules=frozenset(["c", "d"]),
                ),
                Layer(
                    name="level1y",
                    parent=expected_layers[0],
                ),
            ],
        )
        expected_layers.append(
            Layer(
                name="level2",
                parent=expected_layers[2],
                imports=frozenset(["k", "l"]),
            ),
        )

        for layer, expected in zip(layers, expected_layers):
            assert layer.name == expected.name
            assert layer.imports == expected.imports
            assert layer.submodules == expected.submodules

        assert layers[1].parent is layers[0]
        assert layers[2].parent is layers[0]
        assert layers[3].parent is layers[2]


class TestYamlLayersLoader:
    @fixture
    def layers(self) -> Set[Layer]:
        return {Layer("test")}

    @fixture
    def dict_to_layers(self, layers: Set[Layer]) -> DictToLayers:
        def dict_to_layers(
            raw_layer: LayerDict,
            parent: Optional[Layer] = None,
        ) -> Iterator[Layer]:
            return iter(layers)

        return dict_to_layers

    def test_text_io_ok(self, layers: Set[Layer], dict_to_layers: DictToLayers) -> None:
        loader = YamlLayersLoader(dict_to_layers)

        assert set(loader.text_io(StringIO("{}"))) == layers

    def test_text_io_not_a_yaml(
        self, layers: Set[Layer], dict_to_layers: DictToLayers
    ) -> None:
        loader = YamlLayersLoader(dict_to_layers)

        with raises(NotAYamlError):
            loader.text_io(StringIO("- true\nfalse"))

    def test_text_io_not_a_dict(
        self, layers: Set[Layer], dict_to_layers: DictToLayers
    ) -> None:
        loader = YamlLayersLoader(dict_to_layers)

        with raises(NotADictError):
            loader.text_io(StringIO(""))

    @mark.parametrize("is_str", [False, True])
    def test_path(self, layers: Set[Layer], tmp_path: Path, is_str: bool) -> None:
        yml_path = tmp_path / "layers.yml"
        text = "test"

        yml_path.write_text(text)

        class TestYamlLayersLoader(YamlLayersLoader):
            def text_io(self, f: TextIO) -> Set[Layer]:
                assert f.read() == text
                return layers

        path: Union[Path, str]

        if is_str:
            path = str(yml_path)
        else:
            path = yml_path

        assert TestYamlLayersLoader().path(path) is layers
