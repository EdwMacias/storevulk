# Software Tienda

A Django web application with PostgreSQL database for managing store operations.

## Funcionalidades Core
1. Sistema de Autenticación y Roles

Administrador: Acceso completo a todas las funcionalidades
Usuario: Acceso limitado a caja, movimientos y venta de papelería
Login seguro con JWT
Middleware de autorización por rutas

2. Panel Principal (SPA)
Crear un panel único que permita:

Navegación entre módulos sin cambiar de ventana
Indicador permanente del valor actual en caja (siempre visible)
Tabs o sidebar para alternar entre: Papelería, Transacciones, Caja
Dashboard con resumen de actividad del día

3. Módulo de Ventas de Papelería

Catálogo de productos con búsqueda y filtros
Carrito de compras
Procesamiento de ventas con actualización automática de inventario
Generación de recibos/facturas
Actualización inmediata del valor en caja

4. Módulo de Transacciones Bancarias

Registro de transacciones (depósitos, retiros, transferencias)
Selección de entidad bancaria
Campos flexibles (no todos los campos obligatorios)
Categorización de transacciones
Actualización automática de saldos bancarios

5. Sistema de Auditoría y Filtros
Implementar filtros avanzados por:

Rango de fechas
Tipo de transacción (venta, depósito, retiro, etc.)
Entidad bancaria
Monto (rangos)
Usuario que realizó la transacción
Estado de la transacción

## Reportes incluir:

Historial completo de movimientos
Resumen diario/semanal/mensual
Exportación a PDF/Excel

6. Cuadre de Caja

Página dedicada para cuadre diario
Comparación automática entre:

Valor teórico en sistema
Valor físico contado


Registro de diferencias y ajustes
Historial de cuadres anteriores
Validación y cierre de caja diario

7. Importación CSV

Inventario: Carga masiva de productos de papelería
Transacciones: Importación de movimientos bancarios
Validación de datos antes de inserción
Preview de datos antes de confirmar
Manejo de errores y duplicados
Formato de ejemplo y documentación

# Requerimientos Específicos de Implementación
1. Estado Global de Caja

Implementar store global (Redux/Zustand) para el valor actual en caja
Actualización en tiempo real tras cada transacción
Persistencia del estado

2. Validaciones

Validación de saldos (no permitir sobregiros sin autorización)
Verificación de stock antes de ventas
Validación de formatos CSV

3. Seguridad

Sanitización de inputs
Protección contra SQL injection
Rate limiting en APIs
Logs de seguridad para auditoría

4. Experiencia de Usuario

Interfaz intuitiva y rápida
Shortcuts de teclado para operaciones frecuentes
Confirmaciones para operaciones críticas
Indicadores de carga y feedback visual

Entregables Esperados

Django Apps con modelos, vistas y templates
Migraciones de base de datos para todos los modelos
Sistema de autenticación con roles usando Django User
URLs y vistas para todos los módulos
Templates responsivos con el panel dinámico
Funcionalidad de importación CSV con django-import-export
Sistema de reportes con filtros Django
Configuración de Django admin para administración

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package installer)
- virtualenv (recommended)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd softwareTienda
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Install PostgreSQL
- **Ubuntu/Debian**: `sudo apt-get install postgresql postgresql-contrib`
- **macOS**: `brew install postgresql`
- **Windows**: Download from [PostgreSQL official site](https://www.postgresql.org/download/)

#### Create Database

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE softwaretienda;
CREATE USER tienda_user WITH PASSWORD 'your_password';
ALTER ROLE tienda_user SET client_encoding TO 'utf8';
ALTER ROLE tienda_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE tienda_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE softwaretienda TO tienda_user;
\q
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=softwaretienda
DATABASE_USER=tienda_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 6. Django Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files (for production)
python manage.py collectstatic
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Project Structure

```
softwareTienda/
├── manage.py
├── requirements.txt
├── .env
├── softwareTienda/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   └── (Django apps will be created here)
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   └── (HTML templates)
└── media/
    └── (User uploaded files)
```

## Development

### Running Tests

```bash
python manage.py test
```

### Code Style

This project follows PEP 8 style guidelines. Use flake8 for linting:

```bash
flake8 .
```

### Database Migrations

After making model changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Deployment

### Environment Variables for Production

- Set `DEBUG=False`
- Configure `ALLOWED_HOSTS`
- Set secure `SECRET_KEY`
- Configure production database settings
- Set up static file serving
- Configure media file handling

### Database Backup

```bash
pg_dump softwaretienda > backup.sql
```

### Restore Database

```bash
psql softwaretienda < backup.sql
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please contact the development team.