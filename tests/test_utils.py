from types import ModuleType
from unittest.mock import Mock

from pytest import mark

from layer_enforcer.interfaces import Layer
from layer_enforcer.utils import (
    depth,
    is_import_allowed,
    load_factory,
    match_submodule,
    traverse_layers,
)


def test_depth_deep(db: Layer) -> None:
    assert depth(db) == 4


def test_depth_middle(service: Layer) -> None:
    assert depth(service) == 2


def test_is_import_allowed_in(db: Layer, domain: Layer) -> None:
    assert is_import_allowed(db, domain)


def test_is_import_allowed_out(web: Layer, service: Layer) -> None:
    assert not is_import_allowed(service, web)


def test_is_import_allowed_boundary(db: Layer, web: Layer) -> None:
    assert not is_import_allowed(db, web)


def test_is_import_allowed_alien(db: Layer) -> None:
    assert not is_import_allowed(db, Layer("alien"))


def test_load_factory() -> None:
    module = Mock()

    def import_module(s: str) -> ModuleType:
        return module

    assert load_factory("test.module:attr", import_module) is module.attr


@mark.parametrize("module", ["xxx.test", "xxx.test.yyy", "test.yyy", "test"])
def test_match_submodule_match(module: str) -> None:
    assert match_submodule(module, "test")


def test_match_submodule_miss() -> None:
    assert not match_submodule("xxx.tset.yyy", "test")


def test_traverse_layers(
    domain: Layer, service: Layer, infrastructure: Layer, db: Layer
) -> None:
    assert list(traverse_layers(db)) == [db, infrastructure, service, domain]
