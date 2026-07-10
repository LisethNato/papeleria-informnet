from tests.conftest import login
from app.models import Producto, Cliente, Venta


def crear_datos_base(client, db):
    client.post(
        "/productos/nuevo",
        data={"nombre": "Marcador", "descripcion": "Negro", "precio": "1.0", "stock": "20"},
    )
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Cliente Prueba", "email": "cliente@test.com", "telefono": "0977777777", "direccion": "Calle 3"},
    )
    producto = Producto.query.filter_by(nombre="Marcador").first()
    cliente = Cliente.query.filter_by(nombre="Cliente Prueba").first()
    return producto, cliente


def test_registrar_venta_descuenta_stock(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    producto, cliente = crear_datos_base(client, db)

    response = client.post(
        "/ventas/nueva",
        data={
            "cliente_id": str(cliente.id),
            f"cantidad_{producto.id}": "5",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    producto_actualizado = db.session.get(Producto, producto.id)
    assert producto_actualizado.stock == 15

    venta = Venta.query.first()
    assert venta is not None
    assert venta.total == 5.0
    assert venta.cliente_id == cliente.id


def test_venta_no_permite_stock_insuficiente(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    producto, cliente = crear_datos_base(client, db)

    response = client.post(
        "/ventas/nueva",
        data={
            "cliente_id": str(cliente.id),
            f"cantidad_{producto.id}": "999",
        },
        follow_redirects=True,
    )

    assert "insuficiente".encode("utf-8") in response.data

    producto_actualizado = db.session.get(Producto, producto.id)
    assert producto_actualizado.stock == 20


def test_venta_sin_cliente_falla(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    producto, _ = crear_datos_base(client, db)

    response = client.post(
        "/ventas/nueva",
        data={"cliente_id": "", f"cantidad_{producto.id}": "1"},
        follow_redirects=True,
    )

    assert "cliente".encode("utf-8") in response.data


def test_vendedor_puede_registrar_venta(client, db, admin_user, vendedor_user):
    login(client, "admin@test.com", "test1234")
    producto, cliente = crear_datos_base(client, db)
    client.get("/logout")

    login(client, "vendedor@test.com", "test1234")
    response = client.post(
        "/ventas/nueva",
        data={"cliente_id": str(cliente.id), f"cantidad_{producto.id}": "2"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert Venta.query.count() == 1


def test_ver_detalle_venta(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    producto, cliente = crear_datos_base(client, db)
    client.post(
        "/ventas/nueva",
        data={"cliente_id": str(cliente.id), f"cantidad_{producto.id}": "3"},
    )
    venta = Venta.query.first()

    response = client.get(f"/ventas/{venta.id}")
    assert response.status_code == 200
    assert "Marcador".encode("utf-8") in response.data


def test_listar_ventas_requiere_login(client):
    response = client.get("/ventas/", follow_redirects=True)
    assert "Iniciar sesión".encode("utf-8") in response.data


def test_venta_con_multiples_productos(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    producto1, cliente = crear_datos_base(client, db)
    client.post(
        "/productos/nuevo",
        data={"nombre": "Corrector", "descripcion": "Líquido", "precio": "2.0", "stock": "10"},
    )
    producto2 = Producto.query.filter_by(nombre="Corrector").first()

    client.post(
        "/ventas/nueva",
        data={
            "cliente_id": str(cliente.id),
            f"cantidad_{producto1.id}": "2",
            f"cantidad_{producto2.id}": "3",
        },
    )

    venta = Venta.query.first()
    assert len(venta.detalles) == 2
    assert venta.total == (2 * 1.0) + (3 * 2.0)


def test_venta_calcula_total_correctamente(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    producto, cliente = crear_datos_base(client, db)

    client.post(
        "/ventas/nueva",
        data={"cliente_id": str(cliente.id), f"cantidad_{producto.id}": "7"},
    )

    venta = Venta.query.first()
    assert venta.total == 7.0


def test_venta_sin_productos_seleccionados_falla(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    _, cliente = crear_datos_base(client, db)

    response = client.post(
        "/ventas/nueva",
        data={"cliente_id": str(cliente.id)},
        follow_redirects=True,
    )

    assert "al menos un producto".encode("utf-8") in response.data
    assert Venta.query.count() == 0


def test_ver_detalle_venta_inexistente_404(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.get("/ventas/9999")
    assert response.status_code == 404
