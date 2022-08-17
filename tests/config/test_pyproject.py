from dataclasses import asdict
from pathlib import Path

from layer_enforcer.config.interfaces import Config
from layer_enforcer.config.pyproject import (
    CONFIG_PATH,
    PyprojectConfig,
    PyprojectTomlConfigLoader,
    load_pyproject,
)
from layer_enforcer.config.testing import StaticLayersLoader
from layer_enforcer.interfaces import Layer


class TestLoadPyproject:
    def test_not_found(self, tmp_path: Path) -> None:
        expected = asdict(PyprojectConfig())

        assert asdict(load_pyproject(tmp_path / "pyproject.toml")) == expected

    def test_no_tool(self, tmp_path: Path) -> None:
        expected = asdict(PyprojectConfig())
        pyproject_toml = tmp_path / "pyproject.toml"

        pyproject_toml.write_text("x = 123")

        assert asdict(load_pyproject(pyproject_toml)) == expected

    def test_no_tool_layer_enforcer(self, tmp_path: Path) -> None:
        expected = asdict(PyprojectConfig())
        pyproject_toml = tmp_path / "pyproject.toml"

        pyproject_toml.write_text("[tool.test]\n" "x = 123")

        assert asdict(load_pyproject(pyproject_toml)) == expected

    def test_ok(self, tmp_path: Path) -> None:
        expected = asdict(
            PyprojectConfig(
                modules=["test_module1", "test_module2"],
                ignore=["test_moduleX", "test_moduleY"],
                layers="/tmp/layers.yml",
            )
        )
        pyproject_toml = tmp_path / "pyproject.toml"

        pyproject_toml.write_text(
            "[tool.layer_enforcer]\n"
            'modules = ["test_module1", "test_module2"]\n'
            'ignore = ["test_moduleX", "test_moduleY"]\n'
            'layers = "/tmp/layers.yml"'
        )

        assert asdict(load_pyproject(pyproject_toml)) == expected


class TestPyprojectTomlConfigLoader:
    def test_load_none(self) -> None:
        config = Config()
        expected_config = asdict(config)
        pyproject_config = PyprojectConfig(
            modules=[],
            ignore=[],
            layers="",
        )
        layers_loader = StaticLayersLoader()
        loader = PyprojectTomlConfigLoader(
            CONFIG_PATH,
            layers_loader=layers_loader,
            load_pyproject=lambda _: pyproject_config,
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
        pyproject_config = PyprojectConfig(
            modules=["a", "b", "c"],
            ignore=["x", "y"],
            layers="/tmp/layers.yml",
        )
        layers_loader = StaticLayersLoader(path={"/tmp/layers.yml": layers})
        loader = PyprojectTomlConfigLoader(
            CONFIG_PATH,
            layers_loader=layers_loader,
            load_pyproject=lambda _: pyproject_config,
        )
        updated_config = loader.load(config)

        assert asdict(updated_config) == expected_config

    def test_load_no_double_load_pyproject(self) -> None:
        class AlreadyLoadedError(Exception):
            pass

        loaded = False

        def load_pyproject(path: Path) -> PyprojectConfig:
            nonlocal loaded
            if loaded:
                raise AlreadyLoadedError
            return pyproject_config

        config = Config()
        pyproject_config = PyprojectConfig(
            modules=[],
            ignore=[],
            layers="",
        )
        layers_loader = StaticLayersLoader()
        loader = PyprojectTomlConfigLoader(
            CONFIG_PATH,
            layers_loader=layers_loader,
            load_pyproject=load_pyproject,
        )

        loader.load(config)
        loader.load(config)
