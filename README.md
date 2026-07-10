# Papelería INFORMNET

Aplicación web para la gestión de una papelería: control de productos, clientes, ventas y usuarios con roles diferenciados (administrador / vendedor).


## Tecnologías utilizadas

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.13 |
| Framework web | Flask | 3.1.1 |
| ORM | SQLAlchemy (Flask-SQLAlchemy) | 2.0.41 |
| Migraciones | Flask-Migrate (Alembic) | 4.1.0 |
| Autenticación | Flask-Login | 0.6.3 |
| Base de datos | PostgreSQL | 16 / 17 |
| Conector BD | psycopg | 3.2.13 |
| Servidor WSGI (producción) | Gunicorn | 23.0.0 |
| Pruebas | pytest | 8.4.1 |
| Sistema operativo (despliegue) | Ubuntu Server 24.04 LTS | — |
| Plataforma de despliegue | Azure App Service (Linux) | — |

## Funcionalidades

- **Autenticación de usuarios** con inicio y cierre de sesión.
- **Roles de usuario**:
  - **Administrador**: acceso total (crear, editar y eliminar productos, clientes y usuarios).
  - **Vendedor**: puede consultar productos y clientes, y registrar ventas.
- **Gestión de productos**: alta, edición, eliminación y consulta de inventario.
- **Gestión de clientes**: alta, edición, eliminación y consulta.
- **Registro de ventas**: selección de cliente y productos, cálculo automático de totales y descuento de stock en tiempo real.
- **Gestión de usuarios**: el administrador puede crear, editar y eliminar cuentas de vendedores/administradores.
- **Control de acceso por rol** tanto en la interfaz (ocultando acciones no permitidas) como en el servidor (bloqueando el acceso directo por URL con error 403).

## Estructura del proyecto

```
PapeleriaInformnet/
│
├── app/
│   ├── models/              # Modelos de datos (Producto, Cliente, Usuario, Venta, DetalleVenta)
│   ├── routes/              # Blueprints (main, auth, productos, clientes, ventas, usuarios)
│   ├── static/
│   │   └── css/style.css    # Hoja de estilos
│   ├── templates/           # Plantillas Jinja2 (HTML)
│   ├── __init__.py          # Application factory (create_app)
│   ├── extensions.py        # Instancias de db, migrate, login_manager
│   └── utils.py             # Decoradores de permisos (admin_required)
│
├── tests/                   # Suite de pruebas automatizadas (pytest)
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_productos.py
│   ├── test_clientes.py
│   ├── test_ventas.py
│   ├── test_usuarios.py
│   └── test_models.py
│
├── migrations/              # Migraciones generadas por Flask-Migrate/Alembic
├── config.py                # Configuración (Config y TestConfig)
├── run.py                   # Punto de entrada de la aplicación
├── pytest.ini                # Configuración de pytest
├── requirements.txt          # Dependencias del proyecto
├── .env                      # Variables de entorno (no se sube a git)
└── .gitignore
```

## Requisitos previos

- Python 3.11 o superior
- PostgreSQL 16 o 17 instalado localmente (o acceso a una instancia remota)
- Git

## Instalación y configuración local

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd PapeleriaInformnet
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv .venv
```

En Windows (PowerShell):
```bash
.venv\Scripts\Activate.ps1
```

En Mac/Linux:
```bash
source .venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crea un archivo `.env` en la raíz del proyecto con este contenido (ajusta la contraseña y el nombre de usuario según tu instalación de PostgreSQL):

```
SECRET_KEY=una_clave_secreta_segura
DATABASE_URL=postgresql+psycopg://postgres:TU_CONTRASEÑA@localhost:5432/papeleria_db
TEST_DATABASE_URL=postgresql+psycopg://postgres:TU_CONTRASEÑA@localhost:5432/papeleria_test_db
FLASK_APP=run.py
FLASK_ENV=development
```

### 5. Crear las bases de datos en PostgreSQL

Crea dos bases de datos (por ejemplo, usando pgAdmin o `psql`):
- `papeleria_db` — para desarrollo
- `papeleria_test_db` — exclusiva para las pruebas automatizadas

### 6. Aplicar las migraciones

```bash
flask db upgrade
```

### 7. Crear un usuario administrador inicial

```bash
flask shell
```

Dentro de la shell interactiva:

```python
from app.models import Usuario
from app.extensions import db

admin = Usuario(nombre="Administrador", email="admin@papeleria.com", rol="admin")
admin.set_password("una_contraseña_segura")
db.session.add(admin)
db.session.commit()
exit()
```

### 8. Ejecutar la aplicación

```bash
flask run --debug
```

La aplicación estará disponible en `http://127.0.0.1:5000`.

## Ejecutar las pruebas

El proyecto cuenta con una suite de **56 pruebas automatizadas** con pytest, que cubren autenticación, permisos por rol, CRUD de cada módulo y reglas de negocio (descuento de stock, cálculo de totales, restricciones de eliminación).

```bash
pytest -v
```

Las pruebas utilizan la base de datos `papeleria_test_db` (definida en `TEST_DATABASE_URL`), independiente de la base de datos de desarrollo, y limpian las tablas automáticamente antes y después de cada prueba.

## Roles y permisos

| Acción | Administrador | Vendedor |
|---|---|---|
| Ver productos y clientes | ✅ | ✅ |
| Crear / editar / eliminar productos | ✅ | ❌ |
| Crear / editar / eliminar clientes | ✅ | ❌ |
| Registrar ventas | ✅ | ✅ |
| Ver historial de ventas | ✅ | ✅ |
| Gestionar usuarios | ✅ | ❌ |

## Credenciales de acceso para revisión

Para facilitar la evaluación del proyecto, se dispone de una cuenta de acceso con rol de administrador:

| Campo | Valor |
|---|---|
| **URL de acceso** | *(agregar aquí la URL de Azure una vez desplegado, o `http://127.0.0.1:5000/login` en local)* |
| **Correo** | `davidm@papeleria.com` |
| **Contraseña** | `david123` |

> ⚠️ **Nota de seguridad:** esta cuenta se creó únicamente con fines de evaluación académica. No debe reutilizarse esta contraseña en ningún otro sistema. Una vez finalizada la revisión, se recomienda eliminar o cambiar la contraseña de esta cuenta.

## Despliegue en Azure

El proyecto está preparado para desplegarse en **Azure App Service (Linux)** con **Azure Database for PostgreSQL Flexible Server**, sin necesidad de modificar la lógica de la aplicación — únicamente:

1. Configurar las variables de entorno equivalentes desde el panel de Azure App Service.
2. Actualizar `DATABASE_URL` apuntando a la instancia de PostgreSQL en Azure.
3. Publicar el código (por ejemplo, mediante integración continua con GitHub Actions).

## Autor

Proyecto desarrollado por Liseth Nato, para la materia de Cloud Computing.
