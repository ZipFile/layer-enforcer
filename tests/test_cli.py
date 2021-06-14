from pretend import stub

from pytest import fixture, raises

from layer_enforcer.cli import main, parse_args, parse_layers
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


def test_parse_layers(layers_yaml, layers):
    parsed_layers = sorted(parse_layers(layers_yaml), key=lambda l: l.name)
    parent = None

    for parsed, expected in zip(parsed_layers, layers):
        assert parsed.name == expected.name
        assert parsed.imports == expected.imports
        assert parsed.submodules == expected.submodules
        assert parsed.parent == parent

        parent = parsed


def test_parse_args(tmp_path, layers_yaml):
    f = tmp_path / "layers.yaml"
    f.write_text(layers_yaml)

    args = parse_args(["aaa", "bbb", "--layers", str(f)])

    assert args.modules == ["aaa", "bbb"]
    assert args.layers.read() == layers_yaml


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

    with raises(SystemExit):
        main(
            [
                "aaa",
                "bbb",
                "--layers",
                str(f),
                "--ignore",
                "ignored.module,module.ignored",
            ],
            writeln=writeln,
            import_module=import_module,
            match_modules=match_modules,
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

    main(
        ["aaa", "bbb", "--layers", str(f)],
        writeln=writeln,
        import_module=import_module,
        match_modules=match_modules,
    )

    assert out == []
