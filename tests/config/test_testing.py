from pathlib import Path
from typing import Union
from unittest.mock import ANY, sentinel

from pytest import mark

from layer_enforcer.config.testing import (
    NoopConfigLoader,
    StaticConfigLoader,
    StaticLayersLoader,
)
from layer_enforcer.interfaces import Layer


class TestNoopConfigLoader:
    def test_load(self) -> None:
        assert NoopConfigLoader().load(sentinel.config) is sentinel.config


class TestStaticConfigLoader:
    def test_load(self) -> None:
        cl = StaticConfigLoader(sentinel.config)

        assert cl.load(sentinel.default_config) is sentinel.config


class TestStaticLayersLoader:
    def test_text_io_ok(self) -> None:
        layers = {Layer("test")}
        assert StaticLayersLoader(text_io=layers).text_io(ANY) is layers

    def test_text_io_empty(self) -> None:
        assert StaticLayersLoader().text_io(ANY) == set()

    @mark.parametrize("key", [Path("layers.yml"), "layers.yml"])
    def test_path(self, key: Union[Path, str]) -> None:
        layers = {Layer("test")}
        path = {key: layers}

        assert StaticLayersLoader(path=path).path(key) is layers

    def test_path_empty(self) -> None:
        assert StaticLayersLoader(path={}).path("layers.yml") == set()
