from pytest import fixture

from layer_enforcer.interfaces import Layer


@fixture
def domain():
    return Layer("domain", submodules=["domain"])


@fixture
def service(domain):
    return Layer("service", domain, submodules=["services"])


@fixture
def infrastructure(service):
    return Layer(
        "infrastructure",
        service,
        imports=["paramiko", "requests"],
    )


@fixture
def db(infrastructure):
    return Layer(
        "db",
        infrastructure,
        imports=["sqlalchemy", "psycopg2", "alembic"],
        submodules=["models", "memory", "database"],
    )


@fixture
def web(infrastructure):
    return Layer(
        "web",
        infrastructure,
        imports=["fastapi", "jose"],
        submodules=["views", "schemas"],
    )


@fixture
def tasks(infrastructure):
    return Layer(
        "tasks",
        infrastructure,
        imports=["celery"],
        submodules=["tasks"],
    )


@fixture
def layers(db, web, tasks):
    pass
