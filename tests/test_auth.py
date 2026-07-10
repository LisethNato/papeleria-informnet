from tests.conftest import login


def test_login_correcto(client, admin_user):
    response = login(client, "admin@test.com", "test1234")
    assert response.status_code == 200
    assert "Cerrar sesión".encode("utf-8") in response.data


def test_login_incorrecto(client, admin_user):
    response = login(client, "admin@test.com", "clave_mala")
    assert "incorrectos".encode("utf-8") in response.data


def test_logout(client, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.get("/logout", follow_redirects=True)
    assert "Iniciar sesión".encode("utf-8") in response.data


def test_pagina_protegida_sin_login(client):
    response = client.get("/productos/", follow_redirects=True)
    assert "Iniciar sesión".encode("utf-8") in response.data


def test_login_pagina_carga_get(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_usuario_autenticado_redirige_desde_login(client, admin_user):
    login(client, "admin@test.com", "test1234")
    response = client.get("/login", follow_redirects=True)
    # ya logueado, /login debe redirigir al inicio (no mostrar el formulario otra vez)
    assert "Cerrar sesión".encode("utf-8") in response.data


def test_login_con_campos_vacios(client, admin_user):
    response = client.post(
        "/login",
        data={"email": "", "password": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "incorrectos".encode("utf-8") in response.data


def test_ruta_inicio_es_publica(client):
    response = client.get("/")
    assert response.status_code == 200