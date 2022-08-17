from pretend import stub
from pytest import fixture, raises

from layer_enforcer.cli import DEFAULT_LAYER_LOADER, main
from layer_enforcer.config.args import ArgparseConfigLoader
from layer_enforcer.interfaces import Conflict, Layer, Match


@fixture
def layers_yaml():
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
def layers():
    a = Layer("a", imports={"xxx"}, submodules={"aaa"})
    b = Layer("b", a, imports={"yyy"}, submodules={"bbb"})
    c = Layer("c", b, imports={"zzz"}, submodules={"ccc"})
    return [a, b, c]


def test_main(tmp_path, layers_yaml, layers):
    f = tmp_path / "layers.yaml"
    f.write_text(layers_yaml)
    a, b, c = layers
    conflicts = [
        Conflict(
            Match("a", a, [("x", "y"), ("z", "i", "j")], ["test"]),
            Match("b", b, [("z", "y"), ("x", "0")], ["tset"]),
        ),
        Conflict(Match("n", c), Match("m", a)),
        Conflict(Match("ignored.module", c), Match("any", a)),
        Conflict(Match("module.ignored", c), Match("any", a)),
    ]
    fake_tree = stub()
    module = stub(new_grimp_tree=lambda *m: fake_tree)
    out = []

    def import_module(s):
        return module

    def match_modules(tree, layers):
        assert tree is fake_tree
        assert {"a", "b", "c"} == {layer.name for layer in layers}
        return conflicts

    def writeln(s):
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


def test_main_no_conflict(tmp_path, layers_yaml):
    f = tmp_path / "layers.yaml"
    f.write_text(layers_yaml)
    conflicts = []
    fake_tree = stub()
    module = stub(new_grimp_tree=lambda *m: fake_tree)
    out = []

    def import_module(s):
        return module

    def match_modules(tree, layers):
        assert tree is fake_tree
        assert {"a", "b", "c"} == {layer.name for layer in layers}
        return conflicts

    def writeln(s):
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
