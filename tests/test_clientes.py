from tests.conftest import login
from app.models import Cliente


def test_admin_puede_crear_cliente(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    response = client.post(
        "/clientes/nuevo",
        data={"nombre": "Juan Pérez", "email": "juan@test.com", "telefono": "0999999999", "direccion": "Calle 1"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    cliente = Cliente.query.filter_by(nombre="Juan Pérez").first()
    assert cliente is not None


def test_vendedor_no_puede_eliminar_cliente(client, db, vendedor_user, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Ana López", "email": "ana@test.com", "telefono": "0988888888", "direccion": "Calle 2"},
    )
    cliente = Cliente.query.filter_by(nombre="Ana López").first()
    client.get("/logout")

    login(client, "vendedor@test.com", "test1234")
    response = client.post(f"/clientes/eliminar/{cliente.id}")

    assert response.status_code == 403
    assert db.session.get(Cliente, cliente.id) is not None


def test_vendedor_puede_listar_clientes(client, db, vendedor_user):
    login(client, "vendedor@test.com", "test1234")
    response = client.get("/clientes/")
    assert response.status_code == 200


def test_vendedor_no_puede_crear_cliente(client, db, vendedor_user):
    login(client, "vendedor@test.com", "test1234")
    response = client.get("/clientes/nuevo")
    assert response.status_code == 403


def test_admin_puede_editar_cliente(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Pedro Ruiz", "email": "pedro@test.com", "telefono": "0966666666", "direccion": "Calle 3"},
    )
    cliente = Cliente.query.filter_by(nombre="Pedro Ruiz").first()

    client.post(
        f"/clientes/editar/{cliente.id}",
        data={"nombre": "Pedro Ruiz Actualizado", "email": "pedro2@test.com", "telefono": "0955555555", "direccion": "Calle 4"},
    )

    actualizado = db.session.get(Cliente, cliente.id)
    assert actualizado.nombre == "Pedro Ruiz Actualizado"
    assert actualizado.email == "pedro2@test.com"


def test_admin_puede_eliminar_cliente(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Cliente Borrable", "email": "borrable@test.com", "telefono": "0944444444", "direccion": "Calle 5"},
    )
    cliente = Cliente.query.filter_by(nombre="Cliente Borrable").first()

    client.post(f"/clientes/eliminar/{cliente.id}")

    assert db.session.get(Cliente, cliente.id) is None


def test_vendedor_no_puede_editar_cliente(client, db, admin_user, vendedor_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Cliente Protegido", "email": "protegido@test.com", "telefono": "0933333333", "direccion": "Calle 6"},
    )
    cliente = Cliente.query.filter_by(nombre="Cliente Protegido").first()
    client.get("/logout")

    login(client, "vendedor@test.com", "test1234")
    response = client.get(f"/clientes/editar/{cliente.id}")
    assert response.status_code == 403


def test_listar_clientes_requiere_login(client):
    response = client.get("/clientes/", follow_redirects=True)
    assert "Iniciar sesión".encode("utf-8") in response.data


def test_cliente_email_es_opcional(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.post(
        "/clientes/nuevo",
        data={"nombre": "Sin Email", "email": "", "telefono": "0911111111", "direccion": "Calle 7"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    cliente = Cliente.query.filter_by(nombre="Sin Email").first()
    assert cliente is not None


def test_cliente_nuevo_sin_ventas(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Cliente Nuevo", "email": "nuevo@test.com", "telefono": "0922222222", "direccion": "Calle 8"},
    )
    cliente = Cliente.query.filter_by(nombre="Cliente Nuevo").first()
    assert cliente.ventas == []