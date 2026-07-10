from app.models import Usuario, Producto, Cliente, Venta, DetalleVenta


def test_usuario_password_hash_no_es_texto_plano(db):
    usuario = Usuario(nombre="Test", email="hash@test.com", rol="vendedor")
    usuario.set_password("secreto123")

    assert usuario.password_hash != "secreto123"
    assert len(usuario.password_hash) > 20


def test_usuario_check_password_correcta(db):
    usuario = Usuario(nombre="Test", email="check@test.com", rol="vendedor")
    usuario.set_password("secreto123")

    assert usuario.check_password("secreto123") is True


def test_usuario_check_password_incorrecta(db):
    usuario = Usuario(nombre="Test", email="check2@test.com", rol="vendedor")
    usuario.set_password("secreto123")

    assert usuario.check_password("otra_clave") is False


def test_usuario_repr(db):
    usuario = Usuario(nombre="Test", email="repr@test.com", rol="admin")
    usuario.set_password("clave123")
    db.session.add(usuario)
    db.session.commit()

    assert "repr@test.com" in repr(usuario)


def test_producto_repr(db):
    producto = Producto(nombre="Grapadora", descripcion="Metálica", precio=5.0, stock=8)
    db.session.add(producto)
    db.session.commit()

    assert "Grapadora" in repr(producto)


def test_cliente_repr(db):
    cliente = Cliente(nombre="Cliente Repr", email="repr_c@test.com")
    db.session.add(cliente)
    db.session.commit()

    assert "Cliente Repr" in repr(cliente)


def test_venta_repr(db):
    cliente = Cliente(nombre="Cliente Venta", email="cv@test.com")
    usuario = Usuario(nombre="Vendedor", email="vv@test.com", rol="vendedor")
    usuario.set_password("clave123")
    db.session.add_all([cliente, usuario])
    db.session.commit()

    venta = Venta(cliente_id=cliente.id, usuario_id=usuario.id, total=10.0)
    db.session.add(venta)
    db.session.commit()

    assert str(venta.id) in repr(venta)


def test_eliminar_venta_elimina_detalles_pero_no_cliente(db):
    cliente = Cliente(nombre="Cliente Cascada", email="cascada@test.com")
    usuario = Usuario(nombre="Vendedor Cascada", email="vc@test.com", rol="vendedor")
    usuario.set_password("clave123")
    producto = Producto(nombre="Cinta", descripcion="Adhesiva", precio=1.0, stock=10)
    db.session.add_all([cliente, usuario, producto])
    db.session.commit()

    venta = Venta(cliente_id=cliente.id, usuario_id=usuario.id, total=3.0)
    db.session.add(venta)
    db.session.commit()

    detalle = DetalleVenta(
        venta_id=venta.id, producto_id=producto.id,
        cantidad=3, precio_unitario=1.0, subtotal=3.0,
    )
    db.session.add(detalle)
    db.session.commit()
    detalle_id = detalle.id

    db.session.delete(venta)
    db.session.commit()

    assert db.session.get(DetalleVenta, detalle_id) is None
    assert db.session.get(Cliente, cliente.id) is not None