from tests.conftest import login
from app.models import Usuario


def test_admin_puede_listar_usuarios(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.get("/usuarios/")
    assert response.status_code == 200


def test_vendedor_no_puede_listar_usuarios(client, db, vendedor_user):
    login(client, "vendedor@test.com", "test1234")
    response = client.get("/usuarios/")
    assert response.status_code == 403


def test_admin_puede_crear_usuario(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.post(
        "/usuarios/nuevo",
        data={"nombre": "Nuevo Vendedor", "email": "nuevo_v@test.com", "password": "clave123", "rol": "vendedor"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    usuario = Usuario.query.filter_by(email="nuevo_v@test.com").first()
    assert usuario is not None
    assert usuario.rol == "vendedor"


def test_no_permite_email_duplicado(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.post(
        "/usuarios/nuevo",
        data={"nombre": "Duplicado", "email": "admin@test.com", "password": "clave123", "rol": "vendedor"},
        follow_redirects=True,
    )
    assert "Ya existe".encode("utf-8") in response.data
    assert Usuario.query.filter_by(email="admin@test.com").count() == 1


def test_admin_puede_editar_usuario(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/usuarios/nuevo",
        data={"nombre": "Editable", "email": "editable@test.com", "password": "clave123", "rol": "vendedor"},
    )
    usuario = Usuario.query.filter_by(email="editable@test.com").first()

    client.post(
        f"/usuarios/editar/{usuario.id}",
        data={"nombre": "Editado", "email": "editado@test.com", "rol": "admin", "password": ""},
    )

    actualizado = db.session.get(Usuario, usuario.id)
    assert actualizado.nombre == "Editado"
    assert actualizado.rol == "admin"


def test_editar_usuario_sin_cambiar_password(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/usuarios/nuevo",
        data={"nombre": "Mantiene Clave", "email": "mantiene@test.com", "password": "original123", "rol": "vendedor"},
    )
    usuario = Usuario.query.filter_by(email="mantiene@test.com").first()

    client.post(
        f"/usuarios/editar/{usuario.id}",
        data={"nombre": "Mantiene Clave", "email": "mantiene@test.com", "rol": "vendedor", "password": ""},
    )

    actualizado = db.session.get(Usuario, usuario.id)
    assert actualizado.check_password("original123") is True


def test_admin_puede_eliminar_usuario(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    client.post(
        "/usuarios/nuevo",
        data={"nombre": "Borrable", "email": "borrable_u@test.com", "password": "clave123", "rol": "vendedor"},
    )
    usuario = Usuario.query.filter_by(email="borrable_u@test.com").first()

    client.post(f"/usuarios/eliminar/{usuario.id}")

    assert db.session.get(Usuario, usuario.id) is None


def test_admin_no_puede_eliminar_su_propia_cuenta(client, db, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.post(f"/usuarios/eliminar/{admin_user.id}", follow_redirects=True)

    assert "no puedes eliminar tu propia cuenta".encode("utf-8") in response.data.lower()
    assert db.session.get(Usuario, admin_user.id) is not None


def test_vendedor_no_puede_crear_usuario(client, db, vendedor_user):
    login(client, "vendedor@test.com", "test1234")
    response = client.get("/usuarios/nuevo")
    assert response.status_code == 403


def test_listar_usuarios_requiere_login(client):
    response = client.get("/usuarios/", follow_redirects=True)
    assert "Iniciar sesión".encode("utf-8") in response.data