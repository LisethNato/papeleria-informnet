from tests.conftest import login
from app.extensions import db
from app.models import Producto, Cliente, Usuario, Venta, DetalleVenta


# ---------------------- PRODUCTOS ----------------------

def test_producto_guarda_tipos_de_datos_correctos(db):
    producto = Producto(nombre="Cuaderno A4", descripcion="Rayado", precio=3.99, stock=25)
    db.session.add(producto)
    db.session.commit()

    guardado = db.session.get(Producto, producto.id)
    assert isinstance(guardado.nombre, str)
    assert isinstance(guardado.precio, float)
    assert isinstance(guardado.stock, int)
    assert guardado.precio == 3.99
    assert guardado.stock == 25


def test_producto_precio_conserva_decimales(db):
    producto = Producto(nombre="Goma", descripcion="Blanca", precio=0.85, stock=40)
    db.session.add(producto)
    db.session.commit()

    guardado = db.session.get(Producto, producto.id)
    assert guardado.precio == 0.85


def test_producto_descripcion_puede_ser_nula(db):
    producto = Producto(nombre="Sin descripción", precio=1.0, stock=5)
    db.session.add(producto)
    db.session.commit()

    guardado = db.session.get(Producto, producto.id)
    assert guardado.descripcion is None


def test_producto_stock_se_actualiza_tras_venta(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    client.post(
        "/productos/nuevo",
        data={"nombre": "Sacapuntas", "descripcion": "Metálico", "precio": "0.75", "stock": "12"},
    )
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Cliente BD", "email": "clientebd@test.com", "telefono": "0900000000", "direccion": "Calle X"},
    )
    producto = Producto.query.filter_by(nombre="Sacapuntas").first()
    cliente = Cliente.query.filter_by(nombre="Cliente BD").first()

    client.post(
        "/ventas/nueva",
        data={"cliente_id": str(cliente.id), f"cantidad_{producto.id}": "4"},
    )

    guardado = db.session.get(Producto, producto.id)
    assert guardado.stock == 8  # 12 - 4


# ---------------------- CLIENTES ----------------------

def test_cliente_guarda_todos_los_campos(db):
    cliente = Cliente(
        nombre="Cliente Completo",
        email="completo@test.com",
        telefono="0987654321",
        direccion="Av. Siempre Viva 123",
    )
    db.session.add(cliente)
    db.session.commit()

    guardado = db.session.get(Cliente, cliente.id)
    assert guardado.nombre == "Cliente Completo"
    assert guardado.email == "completo@test.com"
    assert guardado.telefono == "0987654321"
    assert guardado.direccion == "Av. Siempre Viva 123"


def test_cliente_campos_opcionales_pueden_ser_nulos(db):
    cliente = Cliente(nombre="Solo Nombre")
    db.session.add(cliente)
    db.session.commit()

    guardado = db.session.get(Cliente, cliente.id)
    assert guardado.email is None
    assert guardado.telefono is None
    assert guardado.direccion is None


# ---------------------- USUARIOS ----------------------

def test_usuario_password_nunca_se_guarda_en_texto_plano(db):
    usuario = Usuario(nombre="Seguridad", email="seguridad@test.com", rol="vendedor")
    usuario.set_password("miClaveSecreta123")
    db.session.add(usuario)
    db.session.commit()

    guardado = db.session.get(Usuario, usuario.id)
    assert guardado.password_hash != "miClaveSecreta123"
    assert "miClaveSecreta123" not in guardado.password_hash


def test_usuario_rol_se_guarda_exactamente_como_se_definio(db):
    usuario = Usuario(nombre="Rol Test", email="roltest@test.com", rol="admin")
    usuario.set_password("clave123")
    db.session.add(usuario)
    db.session.commit()

    guardado = db.session.get(Usuario, usuario.id)
    assert guardado.rol == "admin"


def test_usuario_email_es_unico_en_bd(db):
    u1 = Usuario(nombre="Uno", email="duplicado@test.com", rol="vendedor")
    u1.set_password("clave123")
    db.session.add(u1)
    db.session.commit()

    u2 = Usuario(nombre="Dos", email="duplicado@test.com", rol="vendedor")
    u2.set_password("clave456")
    db.session.add(u2)

    try:
        db.session.commit()
        fallo_constraint = False
    except Exception:
        db.session.rollback()
        fallo_constraint = True

    assert fallo_constraint is True


# ---------------------- VENTAS Y DETALLE_VENTA ----------------------

def test_venta_guarda_relacion_correcta_con_cliente_y_usuario(db):
    cliente = Cliente(nombre="Cliente Rel", email="rel@test.com")
    usuario = Usuario(nombre="Vendedor Rel", email="vendrel@test.com", rol="vendedor")
    usuario.set_password("clave123")
    db.session.add_all([cliente, usuario])
    db.session.commit()

    venta = Venta(cliente_id=cliente.id, usuario_id=usuario.id, total=15.5)
    db.session.add(venta)
    db.session.commit()

    guardada = db.session.get(Venta, venta.id)
    assert guardada.cliente.id == cliente.id
    assert guardada.usuario.id == usuario.id
    assert guardada.total == 15.5


def test_venta_guarda_fecha_automaticamente(db):
    cliente = Cliente(nombre="Cliente Fecha", email="fecha@test.com")
    usuario = Usuario(nombre="Vendedor Fecha", email="vendfecha@test.com", rol="vendedor")
    usuario.set_password("clave123")
    db.session.add_all([cliente, usuario])
    db.session.commit()

    venta = Venta(cliente_id=cliente.id, usuario_id=usuario.id, total=10.0)
    db.session.add(venta)
    db.session.commit()

    guardada = db.session.get(Venta, venta.id)
    assert guardada.fecha is not None


def test_detalle_venta_guarda_subtotal_correcto(db):
    cliente = Cliente(nombre="Cliente Detalle", email="detalle@test.com")
    usuario = Usuario(nombre="Vendedor Detalle", email="venddetalle@test.com", rol="vendedor")
    usuario.set_password("clave123")
    producto = Producto(nombre="Producto Detalle", precio=2.5, stock=10)
    db.session.add_all([cliente, usuario, producto])
    db.session.commit()

    venta = Venta(cliente_id=cliente.id, usuario_id=usuario.id, total=7.5)
    db.session.add(venta)
    db.session.commit()

    detalle = DetalleVenta(
        venta_id=venta.id,
        producto_id=producto.id,
        cantidad=3,
        precio_unitario=2.5,
        subtotal=7.5,
    )
    db.session.add(detalle)
    db.session.commit()

    guardado = db.session.get(DetalleVenta, detalle.id)
    assert guardado.subtotal == 7.5
    assert guardado.cantidad * guardado.precio_unitario == guardado.subtotal


def test_venta_con_varios_detalles_se_guardan_todos(client, db, admin_user):
    login(client, "admin@test.com", "test1234")

    client.post(
        "/productos/nuevo",
        data={"nombre": "ProdA", "descripcion": "A", "precio": "1.0", "stock": "10"},
    )
    client.post(
        "/productos/nuevo",
        data={"nombre": "ProdB", "descripcion": "B", "precio": "2.0", "stock": "10"},
    )
    client.post(
        "/clientes/nuevo",
        data={"nombre": "Cliente Multi", "email": "multi@test.com", "telefono": "0911111111", "direccion": "Calle Y"},
    )

    prod_a = Producto.query.filter_by(nombre="ProdA").first()
    prod_b = Producto.query.filter_by(nombre="ProdB").first()
    cliente = Cliente.query.filter_by(nombre="Cliente Multi").first()

    client.post(
        "/ventas/nueva",
        data={
            "cliente_id": str(cliente.id),
            f"cantidad_{prod_a.id}": "2",
            f"cantidad_{prod_b.id}": "3",
        },
    )

    venta = Venta.query.filter_by(cliente_id=cliente.id).first()
    detalles_guardados = DetalleVenta.query.filter_by(venta_id=venta.id).all()

    assert len(detalles_guardados) == 2
    assert sum(d.subtotal for d in detalles_guardados) == venta.total