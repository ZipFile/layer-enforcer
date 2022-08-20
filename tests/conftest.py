from pytest import fixture

from layer_enforcer.interfaces import Layer


@fixture
def domain() -> Layer:
    return Layer("domain", submodules={"domain"})


@fixture
def service(domain: Layer) -> Layer:
    return Layer("service", domain, submodules={"services"})


@fixture
def infrastructure(service: Layer) -> Layer:
    return Layer(
        "infrastructure",
        service,
        imports={"paramiko", "requests"},
    )


@fixture
def db(infrastructure: Layer) -> Layer:
    return Layer(
        "db",
        infrastructure,
        imports={"sqlalchemy", "psycopg2", "alembic"},
        submodules={"models", "memory", "database"},
    )


@fixture
def web(infrastructure: Layer) -> Layer:
    return Layer(
        "web",
        infrastructure,
        imports={"fastapi", "jose"},
        submodules={"views", "schemas"},
    )


@fixture
def tasks(infrastructure: Layer) -> Layer:
    return Layer(
        "tasks",
        infrastructure,
        imports={"celery"},
        submodules={"tasks"},
    )


@fixture
def layers(db: Layer, web: Layer, tasks: Layer) -> None:
    pass
