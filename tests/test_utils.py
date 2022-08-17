from pretend import stub
from pytest import mark

from layer_enforcer.interfaces import Layer
from layer_enforcer.utils import (
    depth,
    is_import_allowed,
    load_factory,
    match_submodule,
    traverse_layers,
)


def test_depth_deep(db):
    assert depth(db) == 4


def test_depth_middle(service):
    assert depth(service) == 2


def test_is_import_allowed_in(db, domain):
    assert is_import_allowed(db, domain)


def test_is_import_allowed_out(web, service):
    assert not is_import_allowed(service, web)


def test_is_import_allowed_boundary(db, web):
    assert not is_import_allowed(db, web)


def test_is_import_allowed_alien(db):
    assert not is_import_allowed(db, Layer("alien"))


def test_load_factory():
    module = stub(attr=stub())

    def import_module(s):
        return module

    assert load_factory("test.module:attr", import_module) is module.attr


@mark.parametrize("module", ["xxx.test", "xxx.test.yyy", "test.yyy", "test"])
def test_match_submodule_match(module):
    assert match_submodule(module, "test")


def test_match_submodule_miss():
    assert not match_submodule("xxx.tset.yyy", "test")


def test_traverse_layers(domain, service, infrastructure, db):
    assert list(traverse_layers(db)) == [db, infrastructure, service, domain]
