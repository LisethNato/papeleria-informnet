import pytest

from app import create_app
from app.extensions import db as _db
from config import TestConfig
from app.models import Usuario


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def admin_user(db):
    admin = Usuario(nombre="Admin Test", email="admin@test.com", rol="admin")
    admin.set_password("test1234")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def vendedor_user(db):
    vendedor = Usuario(nombre="Vendedor Test", email="vendedor@test.com", rol="vendedor")
    vendedor.set_password("test1234")
    db.session.add(vendedor)
    db.session.commit()
    return vendedor


def login(client, email, password):
    return client.post(
        "/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )