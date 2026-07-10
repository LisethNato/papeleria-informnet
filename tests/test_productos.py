from tests.conftest import login
from app.models import Producto


def test_admin_puede_crear_producto(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    response = client.post(
        "/productos/nuevo",
        data={"nombre": "Cuaderno", "descripcion": "100 hojas", "precio": "2.5", "stock": "10"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    producto = Producto.query.filter_by(nombre="Cuaderno").first()
    assert producto is not None
    assert producto.stock == 10


def test_vendedor_no_puede_crear_producto(client, db, vendedor_user):
    login(client, "vendedor@test.com", "test1234")

    response = client.get("/productos/nuevo")
    assert response.status_code == 403


def test_listar_productos_requiere_login(client):
    response = client.get("/productos/", follow_redirects=True)
    assert "Iniciar sesión".encode("utf-8") in response.data


def test_admin_puede_editar_producto(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    client.post(
        "/productos/nuevo",
        data={"nombre": "Lápiz", "descripcion": "HB", "precio": "0.5", "stock": "100"},
    )
    producto = Producto.query.filter_by(nombre="Lápiz").first()

    client.post(
        f"/productos/editar/{producto.id}",
        data={"nombre": "Lápiz HB2", "descripcion": "HB2", "precio": "0.6", "stock": "90"},
    )

    actualizado = db.session.get(Producto, producto.id)
    assert actualizado.nombre == "Lápiz HB2"
    assert actualizado.stock == 90


def test_admin_puede_eliminar_producto(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    client.post(
        "/productos/nuevo",
        data={"nombre": "Borrador", "descripcion": "Blanco", "precio": "0.3", "stock": "50"},
    )
    producto = Producto.query.filter_by(nombre="Borrador").first()

    client.post(f"/productos/eliminar/{producto.id}")

    eliminado = db.session.get(Producto, producto.id)
    assert eliminado is None


def test_vendedor_puede_listar_productos(client, db, vendedor_user):
    login(client, "vendedor@test.com", "test1234")

    response = client.get("/productos/")
    assert response.status_code == 200


def test_vendedor_no_puede_editar_producto(client, db, admin_user, vendedor_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/productos/nuevo",
        data={"nombre": "Regla", "descripcion": "30cm", "precio": "1.0", "stock": "20"},
    )
    producto = Producto.query.filter_by(nombre="Regla").first()
    client.get("/logout")

    login(client, "vendedor@test.com", "test1234")
    response = client.get(f"/productos/editar/{producto.id}")
    assert response.status_code == 403


def test_vendedor_no_puede_eliminar_producto(client, db, admin_user, vendedor_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/productos/nuevo",
        data={"nombre": "Tijera", "descripcion": "Escolar", "precio": "1.5", "stock": "15"},
    )
    producto = Producto.query.filter_by(nombre="Tijera").first()
    client.get("/logout")

    login(client, "vendedor@test.com", "test1234")
    response = client.post(f"/productos/eliminar/{producto.id}")
    assert response.status_code == 403
    assert db.session.get(Producto, producto.id) is not None


def test_listar_productos_vacio(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.get("/productos/")
    assert response.status_code == 200


def test_crear_producto_con_precio_decimal(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    client.post(
        "/productos/nuevo",
        data={"nombre": "Resaltador", "descripcion": "Amarillo", "precio": "1.75", "stock": "30"},
    )

    producto = Producto.query.filter_by(nombre="Resaltador").first()
    assert producto is not None
    assert producto.precio == 1.75