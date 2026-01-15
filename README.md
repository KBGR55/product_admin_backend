# Product Admin - Backend

Sistema de administración de productos y organizaciones con gestión de empleados y roles. Construido con Python, Pyramid y SQLAlchemy.

## Características

- **Gestión de Usuarios**: Registro, autenticación y perfiles de usuario
- **Gestión de Organizaciones**: Crear, actualizar y eliminar organizaciones con marca personalizada
- **Gestión de Empleados**: Agregar y gestionar empleados dentro de organizaciones
- **Sistema de Roles**: Crear roles y asignar a empleados
- **Gestión de Productos**: CRUD completo de productos con atributos personalizados
- **Autenticación JWT**: Seguridad mediante tokens JWT
- **CORS Habilitado**: Integración con frontend en Next.js

## Requisitos Previos

- Python 3.9+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/product-admin-backend.git
cd product-admin-backend
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
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
# Crear la base de datos
createdb product_admin

# Las tablas se crearán automáticamente al iniciar la aplicación
```

## Ejecución

```bash
python main.py
```

El servidor estará disponible en `http://localhost:6543`

## Estructura del Proyecto

```
product-admin-backend/
├── app/
│   ├── models/
│   │   ├── user.py              # Modelo de usuarios
│   │   ├── account.py           # Modelo de cuentas
│   │   ├── organization.py      # Modelos de organizaciones, empleados y roles
│   │   └── product.py           # Modelo de productos
│   ├── views/
│   │   ├── user_views.py        # Vistas de usuarios
│   │   ├── account_views.py     # Vistas de autenticación
│   │   ├── organization_views.py # Vistas de organizaciones
│   │   └── product_views.py     # Vistas de productos
│   ├── middleware/
│   │   └── jwt_middleware.py    # Middleware de autenticación JWT
│   ├── database.py              # Configuración de base de datos
│   └── __init__.py
├── __init__.py                  # Configuración principal de Pyramid
├── main.py                      # Punto de entrada
├── requirements.txt             # Dependencias del proyecto
└── .env.example                 # Variables de entorno ejemplo
```

## Endpoints principales

### Usuarios
- `POST /api/users` - Crear usuario
- `GET /api/users/{id}` - Obtener usuario
- `GET /api/users` - Listar usuarios
- `PUT /api/users/{id}` - Actualizar usuario
- `DELETE /api/users/{id}` - Eliminar usuario

### Cuentas & Autenticación
- `POST /api/accounts/register` - Registrar cuenta
- `POST /api/accounts/login` - Login
- `PUT /api/accounts/change-password` - Cambiar contraseña

### Organizaciones
- `POST /api/organizations` - Crear organización
- `GET /api/organizations/{org_id}` - Obtener organización
- `GET /api/organizations` - Listar organizaciones del usuario
- `PUT /api/organizations/{org_id}` - Actualizar organización
- `DELETE /api/organizations/{org_id}` - Eliminar organización

### Empleados
- `POST /api/organizations/{org_id}/employees` - Agregar empleado
- `GET /api/organizations/{org_id}/employees` - Listar empleados
- `DELETE /api/organizations/{org_id}/employees/{employee_id}` - Remover empleado

### Roles
- `POST /api/organizations/{org_id}/roles` - Crear rol
- `GET /api/organizations/{org_id}/roles` - Listar roles
- `POST /api/organizations/{org_id}/employees/{employee_id}/roles/{role_id}` - Asignar rol
- `DELETE /api/organizations/{org_id}/employees/{employee_id}/roles/{role_id}` - Remover rol

### Productos
- `POST /api/organizations/{org_id}/products` - Crear producto
- `GET /api/organizations/{org_id}/products/{product_id}` - Obtener producto
- `GET /api/organizations/{org_id}/products` - Listar productos
- `PUT /api/organizations/{org_id}/products/{product_id}` - Actualizar producto
- `DELETE /api/organizations/{org_id}/products/{product_id}` - Eliminar producto

## Autenticación

La API utiliza JWT (JSON Web Tokens) para autenticación. Incluye el token en el header:

```bash
Authorization: Bearer <tu-token-jwt>
```

## Modelos de Base de Datos

### Usuario
- ID, Nombre, Apellido, Fecha de nacimiento
- Tipo de identidad (RUC, DNI, Pasaporte, etc)
- Número de identidad único
- Género, Estado activo

### Organización
- Nombre, Email, Razón social, Tipo
- Descripción, Dirección
- Colores de marca (Primario, Secundario, Terciario)
- URL de logo, Contador de empleados
- Datos extra (JSON)
- Estado activo
- Propietario (FK Usuario)

### Empleado de Organización
- Organización (FK), Usuario (FK)
- Estado activo
- Muchos a muchos con Roles

### Rol de Organización
- Nombre, Descripción
- Organización (FK)
- Muchos a muchos con Empleados

### Producto
- Nombre, Descripción, SKU (único)
- Precio, Costo, Stock
- URL de foto
- Atributos personalizados (JSON)
- Estado activo
- Organización (FK)

## Tecnologías Utilizadas

- **Framework**: Pyramid
- **ORM**: SQLAlchemy
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (PyJWT)
- **Validación**: Marshmallow (opcional)
- **Hashing**: bcrypt

## Dependencias principales

```
pyramid==2.0
sqlalchemy==2.0
psycopg2-binary==2.9
pyjwt==2.8
bcrypt==4.0
```

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.



## Enlaces útiles

- [Frontend Repository](https://github.com/KBGR55/product_admin_frontend)
- [Documentación de Pyramid](https://docs.pylonsproject.org/projects/pyramid/)
- [Documentación de SQLAlchemy](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

Si te fue útil, considera dar una estrella en GitHub!