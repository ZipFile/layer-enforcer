from pathlib import Path
from types import ModuleType
from typing import Collection, Iterable, List
from unittest.mock import Mock

from pytest import fixture, raises

from layer_enforcer.cli import DEFAULT_LAYER_LOADER, main
from layer_enforcer.config.args import ArgparseConfigLoader
from layer_enforcer.config.testing import NoopConfigLoader
from layer_enforcer.interfaces import Conflict, Layer, Match, Tree


@fixture
def layers_yaml() -> str:
    return """
    name: a
    imports: ["xxx"]
    submodules: ["aaa"]
    layers:
    - name: b
      imports: ["yyy"]
      submodules: ["bbb"]
      layers:
      - name: c
        imports: ["zzz"]
        submodules: ["ccc"]
    """


@fixture
def layers() -> List[Layer]:
    a = Layer("a", imports={"xxx"}, submodules={"aaa"})
    b = Layer("b", a, imports={"yyy"}, submodules={"bbb"})
    c = Layer("c", b, imports={"zzz"}, submodules={"ccc"})

    return [a, b, c]


def test_main(tmp_path: Path, layers_yaml: str, layers: List[Layer]) -> None:
    f = tmp_path / "layers.yaml"
    f.write_text(layers_yaml)
    a, b, c = layers
    conflicts = [
        Conflict(
            Match("a", a, [("x", "y"), ("z", "i", "j")], {"test"}),
            Match("b", b, [("z", "y"), ("x", "0")], {"tset"}),
        ),
        Conflict(Match("n", c), Match("m", a)),
        Conflict(Match("ignored.module", c), Match("any", a)),
        Conflict(Match("module.ignored", c), Match("any", a)),
    ]
    module = Mock()
    out = []

    def import_module(s: str) -> ModuleType:
        return module

    def match_modules(tree: Tree, layers: Collection[Layer]) -> Iterable[Conflict]:
        assert tree is module.new_grimp_tree.return_value
        assert {"a", "b", "c"} == {layer.name for layer in layers}
        return conflicts

    def writeln(s: str) -> None:
        out.append(s)

    config_loader = ArgparseConfigLoader(
        [
            "aaa",
            "bbb",
            "--layers",
            str(f),
            "--ignore",
            "ignored.module,module.ignored",
        ],
        layers_loader=DEFAULT_LAYER_LOADER,
    )

    with raises(SystemExit):
        main(
            writeln=writeln,
            import_module=import_module,
            match_modules=match_modules,
            config_loader=config_loader,
        )

    assert out == [
        "a:",
        "  Main layer: a",
        "    x -> y",
        "    z -> i -> j",
        "  Conflicts with: b",
        "    z -> y",
        "    x -> 0",
        "",
        "n:",
        "  Main layer: c",
        "  Conflicts with: a",
        "",
    ]


def test_main_no_conflict(tmp_path: Path, layers_yaml: str) -> None:
    f = tmp_path / "layers.yaml"
    f.write_text(layers_yaml)
    conflicts: List[Conflict] = []
    module = Mock()
    out = []

    def import_module(s: str) -> ModuleType:
        return module

    def match_modules(tree: Tree, layers: Collection[Layer]) -> Iterable[Conflict]:
        assert tree is module.new_grimp_tree.return_value
        assert {"a", "b", "c"} == {layer.name for layer in layers}
        return conflicts

    def writeln(s: str) -> None:
        out.append(s)

    config_loader = ArgparseConfigLoader(
        ["aaa", "bbb", "--layers", str(f)],
        layers_loader=DEFAULT_LAYER_LOADER,
    )

    main(
        writeln=writeln,
        import_module=import_module,
        match_modules=match_modules,
        config_loader=config_loader,
    )

    assert out == []


def test_main_no_modules() -> None:
    out = []

    def import_module(s: str) -> ModuleType:
        assert False, "should not be reached"

    def match_modules(tree: Tree, layers: Collection[Layer]) -> Iterable[Conflict]:
        assert False, "should not be reached"

    def writeln(s: str) -> None:
        out.append(s)

    with raises(SystemExit):
        main(
            writeln=writeln,
            import_module=import_module,
            match_modules=match_modules,
            config_loader=NoopConfigLoader(),
        )

    assert out == ["No modules to check."]
