from dataclasses import asdict
from io import StringIO, TextIOBase
from pathlib import Path
from typing import List

from layer_enforcer.config.args import ArgparseConfigLoader, Args, parse_args
from layer_enforcer.config.interfaces import Config
from layer_enforcer.config.testing import StaticLayersLoader
from layer_enforcer.interfaces import Layer


class TestParseArgs:
    def test_ok(self, tmp_path: Path) -> None:
        layers_yml = tmp_path / "layers.yml"
        layers_yml.write_text("name: test")
        args = parse_args(
            [
                "test_module1",
                "test_module2",
                "--layers",
                str(layers_yml),
                "--ignore",
                "test_moduleX,test_moduleY",
            ]
        )

        assert args.modules == ["test_module1", "test_module2"]
        assert args.ignore == {"test_moduleX", "test_moduleY"}
        assert isinstance(args.layers, TextIOBase)
        assert args.layers.read() == "name: test"


class TestArgparseConfigLoader:
    def test_load_none(self) -> None:
        config = Config()
        expected_config = asdict(config)
        args = Args(
            modules=[],
            layers=None,
            ignore=set(),
        )
        layers_loader = StaticLayersLoader()
        loader = ArgparseConfigLoader(
            [],
            layers_loader=layers_loader,
            parse_args=lambda _: args,
        )
        updated_config = loader.load(config)

        assert asdict(updated_config) == expected_config

    def test_load_all(self) -> None:
        layers = {Layer("test")}
        config = Config()
        expected_config = asdict(
            Config(
                modules={"a", "b", "c"},
                layers=layers,
                ignore={"x", "y"},
            )
        )
        args = Args(
            modules=["a", "b", "c"],
            layers=StringIO(""),
            ignore={"x", "y"},
        )
        layers_loader = StaticLayersLoader(text_io=layers)
        loader = ArgparseConfigLoader(
            [],
            layers_loader=layers_loader,
            parse_args=lambda _: args,
        )
        updated_config = loader.load(config)

        assert asdict(updated_config) == expected_config

    def test_load_no_double_parse(self) -> None:
        class AlreadyParsedError(Exception):
            pass

        parsed = False

        def parse_args(argv: List[str]) -> Args:
            nonlocal parsed
            if parsed:
                raise AlreadyParsedError
            return args

        config = Config()
        args = Args(
            modules=[],
            layers=StringIO(""),
            ignore=set(),
        )
        layers_loader = StaticLayersLoader()
        loader = ArgparseConfigLoader(
            [],
            layers_loader=layers_loader,
            parse_args=parse_args,
        )

        loader.load(config)
        loader.load(config)
