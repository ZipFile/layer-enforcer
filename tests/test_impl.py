from typing import List, NamedTuple, Tuple

from pytest import fixture, mark

from layer_enforcer.impl import match_layer, match_modules
from layer_enforcer.interfaces import Layer, Tree


@fixture
def layers():
    root = Layer("root", submodules={"_r"})
    svc = Layer("svc", root, submodules={"_s"})
    web = Layer("web", svc, imports={"w"}, submodules={"_w"})
    db = Layer("db", svc, imports={"d"}, submodules={"_d"})

    return [root, svc, web, db]


class FakeTree(Tree):
    def __init__(self, import_chains, prefix="t"):
        self.modules = {
            import_
            for import_chain in import_chains
            for import_ in import_chain
            if import_ == prefix or import_.startswith(f"{prefix}.")
        }
        self.chains = {
            (import_chain[i], import_chain[j]): import_chain[i : j + 1]
            for import_chain in import_chains
            for i in range(len(import_chain))
            for j in range(i + 1, len(import_chain))
        }

    def walk(self):
        return iter(sorted(self.modules))

    def find_chains(self, importer, imported):
        try:
            yield self.chains[importer, imported]
        except KeyError:
            pass

    def find_upstream_modules(self, module):
        modules = set()

        for chain in self.chains:
            if chain[0] == module:
                modules.update(chain[1:])

        return modules


def test_match_layer_no_match():
    tree = FakeTree([])
    layer = Layer("test", None, {"test"}, {"test"})

    assert not match_layer(tree, layer, "tset")


def test_match_layer_imports():
    tree = FakeTree([("test", "zzz", "xxx")])
    layer = Layer("test", None, {"xxx"}, set())

    assert match_layer(tree, layer, "test")


def test_match_layer_submodule():
    tree = FakeTree([])
    layer = Layer("test", None, set(), {"test"})

    assert match_layer(tree, layer, "nested.test.xxx")


class Result(NamedTuple):
    module: str
    layer: str
    chains: List[Tuple[str, ...]]


class Pair(NamedTuple):
    a: Result
    b: Result


@mark.parametrize(
    ["chains", "expected"],
    [
        (
            [("t.x", "w"), ("t.x", "d"), ("t.x", "t._s")],
            [
                Pair(
                    Result("t.x", "db", [("t.x", "d")]),
                    Result("t.x", "web", [("t.x", "w")]),
                ),
            ],
        ),
        (
            [
                ("t.a", "t._w"),
                ("t.a", "t.b", "t._d"),
                ("t._r", "t.b"),
            ],
            [
                Pair(
                    Result("t.a", "db", [("t.a", "t.b", "t._d")]),
                    Result("t.a", "web", [("t.a", "t._w")]),
                ),
                Pair(
                    Result("t._r", "root", []),
                    Result("t._r", "db", [("t._r", "t.b")]),
                ),
            ],
        ),
    ],
    ids=["double_layered", "infect"],
)
def test_match_modules(chains, expected, layers):
    tree = FakeTree(chains)

    result = [
        Pair(
            Result(c.main.module, c.main.layer.name, c.main.chains),
            Result(c.dupe.module, c.dupe.layer.name, c.dupe.chains),
        )
        for c in match_modules(tree, layers)
    ]
    assert result == expected
