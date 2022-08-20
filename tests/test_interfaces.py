from typing import List, Set, Tuple

from pytest import mark

from layer_enforcer.interfaces import Layer, Match


def test_layer_repr() -> None:
    assert repr(Layer("test")) == repr("test")


@mark.parametrize(
    ["chains", "submodules", "expected"],
    [
        ([], set(), False),
        ([("a", "b")], set(), True),
        ([], {"x", "y"}, True),
        ([("a", "b")], {"x", "y"}, True),
    ],
)
def test_match_bool(
    chains: List[Tuple[str, ...]], submodules: Set[str], expected: bool, domain: Layer
) -> None:
    assert bool(Match("test", domain, chains, submodules)) == expected
