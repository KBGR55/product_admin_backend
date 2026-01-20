# Product Admin – Backend

Sistema de administración de productos y organizaciones con gestión de empleados y roles. Construido con **Python**, **Pyramid** y **SQLAlchemy**.

---

## Características

* **Gestión de Usuarios**: Registro, autenticación y perfiles de usuario
* **Gestión de Organizaciones**: Crear, actualizar y eliminar organizaciones con marca personalizada
* **Gestión de Empleados**: Agregar y gestionar empleados dentro de organizaciones
* **Sistema de Roles**: Crear roles y asignar a empleados
* **Gestión de Productos**: CRUD completo de productos con atributos personalizados
* **Autenticación JWT**: Seguridad mediante tokens JWT
* **CORS Habilitado**: Integración con frontend en Next.js

---

## Requisitos Previos

* Python **3.10+**
* PostgreSQL **12+**
* pip

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/product-admin-backend.git
cd product_admin_backend
```

### 2. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/product_admin

# JWT
JWT_SECRET=tu-secret-key-aqui
JWT_ALGORITHM=HS256

# CORS
CORS_ORIGIN=http://localhost:3000
```

### 5. Configurar Base de Datos

```bash
createdb product_admin
# Las tablas se crean automáticamente al iniciar la aplicación
```

---

## Ejecución

```bash
python main.py
```

Servidor disponible en:

```
http://localhost:6543
```

---

## Estructura del Proyecto

```text
product_admin_backend/
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── account.py
│   │   ├── organization.py
│   │   └── product.py
│   ├── views/
│   │   ├── user_views.py
│   │   ├── account_views.py
│   │   ├── organization_views.py
│   │   └── product_views.py
│   ├── middleware/
│   │   └── jwt_middleware.py
│   ├── database.py
│   └── __init__.py
├── main.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Endpoints Principales

### Usuarios

* `POST /api/users`
* `GET /api/users/{id}`
* `GET /api/users`
* `PUT /api/users/{id}`
* `DELETE /api/users/{id}`

### Autenticación

* `POST /api/accounts/register`
* `POST /api/accounts/login`
* `PUT /api/accounts/change-password`

### Organizaciones

* `POST /api/organizations`
* `GET /api/organizations/{org_id}`
* `GET /api/organizations`
* `PUT /api/organizations/{org_id}`
* `DELETE /api/organizations/{org_id}`

### Productos

* `POST /api/organizations/{org_id}/products`
* `GET /api/organizations/{org_id}/products`
* `GET /api/organizations/{org_id}/products/{product_id}`
* `PUT /api/organizations/{org_id}/products/{product_id}`
* `DELETE /api/organizations/{org_id}/products/{product_id}`

---

## Autenticación

Incluir el token JWT en el header:

```http
Authorization: Bearer <token>
```

---

## Tecnologías

* **Framework**: Pyramid 2.0.2
* **ORM**: SQLAlchemy 1.4.x
* **Base de Datos**: PostgreSQL
* **Autenticación**: PyJWT
* **Hashing**: bcrypt

---

## Dependencias Principales

```txt
pyramid==2.0.2
SQLAlchemy==1.4.46
psycopg2-binary==2.9.11
python-dotenv==0.19.2
requests==2.25.1
waitress==3.0.2
bcrypt==5.0.0
PyJWT==2.3.0
```

---

## Contribuir

1. Fork del proyecto
2. Crear rama (`git checkout -b feature/nueva-feature`)
3. Commit (`git commit -m 'feat: nueva feature'`)
4. Push (`git push origin feature/nueva-feature`)
5. Pull Request

---

## Licencia

MIT

---

## Enlaces

* Frontend: [https://github.com/KBGR55/product_admin_frontend](https://github.com/KBGR55/product_admin_frontend)
* Pyramid: [https://docs.pylonsproject.org/projects/pyramid/](https://docs.pylonsproject.org/projects/pyramid/)
* SQLAlchemy: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)
* PostgreSQL: [https://www.postgresql.org/docs/](https://www.postgresql.org/docs/)
