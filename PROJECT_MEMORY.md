# Software Tienda - Project Memory

## Project Overview
A comprehensive point-of-sale system for a store management platform built with Django. The system handles multiple business operations including cash register management, transactions, user administration, and is designed to expand to include stationery sales (papelería) and banking operations.

## Technology Stack
- **Backend**: Django 5.2.6 with PostgreSQL database
- **Frontend**: Django templates with Bootstrap 5 (via crispy-forms)
- **Environment**: python-decouple for configuration management
- **Styling**: crispy-bootstrap5 for form rendering

## Project Structure
```
softwareTienda/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── PROJECT_MEMORY.md        # This file - comprehensive project documentation
├── CLAUDE.md                # Development commands and instructions
├── softwareTienda/          # Main Django project
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI application
├── accounts/                # User authentication and role management
├── main/                    # Core business logic app (placeholder)
├── caja/                    # Cash register and transaction management
├── static/                  # Static assets (CSS, JS, images)
├── templates/               # Django HTML templates
└── media/                   # User uploaded files
```

## Completed Modules

### 1. Authentication System (accounts/)
**Status**: ✅ Complete
**Features Implemented**:
- Custom User model with role-based access (Admin/User)
- Secure login/logout functionality
- Admin-only user creation (signup hidden from regular users)
- Comprehensive user management panel for administrators
- Role-based middleware for access control
- Professional admin interface with user statistics

**Key Files**:
- `accounts/models.py` - Custom User model with roles
- `accounts/views.py` - Authentication views and admin user management
- `accounts/forms.py` - Custom forms for user creation and login
- `accounts/decorators.py` - Role-based access decorators
- `accounts/middleware.py` - Role-based access middleware
- `templates/accounts/admin/` - Admin user management templates

**URLs**:
- `/accounts/login/` - User login
- `/accounts/logout/` - User logout
- `/accounts/admin/` - Admin dashboard
- `/accounts/admin/users/` - User management
- `/accounts/admin/users/create/` - Create new users
- `/accounts/admin/users/<id>/edit/` - Edit users
- `/accounts/admin/users/<id>/delete/` - Delete users

### 2. Cash Register System (caja/)
**Status**: ✅ Complete with Advanced Features
**Features Implemented**:

#### Core Functionality
- Complete cash register lifecycle (open/close)
- Income and outcome transaction recording
- Real-time balance calculation
- Multi-user support with user tracking
- Commission tracking (percentage and fixed)
- Bank and entity integration

#### Transaction Management
- **Transaction Types**: Income and Outcome
- **Payment Methods**: Cash, Transfer, Card, Check, Digital Wallet, Other
- **Transaction Categories**:
  - General Transactions
  - Papelería Sales (ready for future module)
  - Bank Operations
  - Commission Income
  - Operational Expenses
  - Supply Expenses
  - Cash Adjustments
  - Other Income/Expenses

#### Advanced Reporting System
- **Comprehensive Closing Reports**: Detailed shift analysis
- **Income Breakdown by Category**: Shows earnings from each business area
- **Payment Method Analysis**: Breakdown by payment type
- **Cash Reconciliation**: Physical count vs system calculation
- **Discrepancy Detection**: Automatic identification of cash differences
- **Performance Metrics**: Average per transaction, shift duration
- **Print-Ready Reports**: Professional closing reports

#### Business Intelligence
- Multi-source income tracking
- Historical data storage
- Audit trail for all operations
- Commission tracking and reporting
- Net profit calculations

**Key Models**:
- `Bank` - Bank information management
- `Entity` - Flexible entity system (banks, payment platforms, etc.)
- `CashRegister` - Cash register session management
- `Transaction` - Comprehensive transaction recording
- `CashRegisterReport` - Detailed closing reports

**Key Files**:
- `caja/models.py` - Database models for cash operations
- `caja/views.py` - Views for cash register management
- `caja/forms.py` - Forms including cash reconciliation
- `caja/admin.py` - Django admin configuration
- `templates/caja/` - Cash register interface templates

**URLs**:
- `/caja/` - Cash register dashboard
- `/caja/abrir/` - Open cash register
- `/caja/cerrar/<id>/` - Close cash register with reconciliation
- `/caja/reporte/<id>/` - View detailed closing report
- `/caja/transacciones/` - Transaction history
- `/caja/transacciones/nueva/` - Create new transaction
- `/caja/transacciones/nueva/<type>/` - Quick income/outcome entry

### 3. Navigation and UI
**Status**: ✅ Complete
**Features Implemented**:
- Role-based navigation menu
- Point of Sale dropdown for authenticated users
- Admin-only sections for user management
- Responsive Bootstrap 5 design
- Professional styling with icons

## Database Schema

### User Management
```sql
-- Custom User model (extends AbstractUser)
User {
    id: AutoField
    username: CharField
    email: EmailField
    first_name: CharField
    last_name: CharField
    role: CharField(choices=['admin', 'user'])
    created_at: DateTimeField
    updated_at: DateTimeField
    is_active: BooleanField
    last_login: DateTimeField
}
```

### Cash Register System
```sql
-- Bank entities
Bank {
    id: AutoField
    name: CharField(100)
    code: CharField(10, unique=True)
    is_active: BooleanField
    created_at: DateTimeField
    updated_at: DateTimeField
}

-- General entities (banks, payment platforms, etc.)
Entity {
    id: AutoField
    name: CharField(100)
    entity_type: CharField(choices=['bank', 'payment_platform', 'cash', 'other'])
    code: CharField(20, unique=True)
    description: TextField
    is_active: BooleanField
    created_at: DateTimeField
    updated_at: DateTimeField
}

-- Cash register sessions
CashRegister {
    id: AutoField
    name: CharField(100)
    opening_balance: DecimalField(12,2)
    current_balance: DecimalField(12,2)
    status: CharField(choices=['open', 'closed', 'suspended'])
    opened_by: ForeignKey(User)
    closed_by: ForeignKey(User, null=True)
    opened_at: DateTimeField(null=True)
    closed_at: DateTimeField(null=True)
    notes: TextField
    created_at: DateTimeField
    updated_at: DateTimeField
}

-- Individual transactions
Transaction {
    id: AutoField
    transaction_type: CharField(choices=['income', 'outcome'])
    amount: DecimalField(12,2)
    description: CharField(255)
    category: CharField(25, choices=[...])
    payment_method: CharField(20, choices=[...])
    bank: ForeignKey(Bank, null=True)
    entity: ForeignKey(Entity, null=True)
    commission: DecimalField(10,2)
    commission_percentage: DecimalField(5,2)
    reference_number: CharField(50)
    notes: TextField
    cash_register: ForeignKey(CashRegister, null=True)
    user: ForeignKey(User)
    transaction_date: DateTimeField
    created_at: DateTimeField
    updated_at: DateTimeField
}

-- Comprehensive closing reports
CashRegisterReport {
    id: AutoField
    cash_register: OneToOneField(CashRegister)
    opening_balance: DecimalField(12,2)
    closing_balance: DecimalField(12,2)
    total_income: DecimalField(12,2)
    total_outcome: DecimalField(12,2)
    total_commissions: DecimalField(12,2)
    -- Category breakdowns
    papeleria_income: DecimalField(12,2)
    bank_operations_income: DecimalField(12,2)
    commission_income: DecimalField(12,2)
    general_transactions_income: DecimalField(12,2)
    other_income: DecimalField(12,2)
    -- Payment method breakdowns
    cash_total: DecimalField(12,2)
    transfer_total: DecimalField(12,2)
    card_total: DecimalField(12,2)
    other_payment_total: DecimalField(12,2)
    -- Cash reconciliation
    physical_cash_count: DecimalField(12,2, null=True)
    cash_difference: DecimalField(12,2)
    -- Metadata
    transaction_count: IntegerField
    shift_duration_minutes: IntegerField(null=True)
    notes: TextField
    created_at: DateTimeField
}
```

## Business Logic Features

### Security & Access Control
- **Role-based access**: Admin vs User permissions
- **Signup restrictions**: Only admins can create users
- **Session tracking**: Complete audit trail of who opened/closed registers
- **Access middleware**: Automatic enforcement of role restrictions

### Financial Management
- **Multi-currency support**: Decimal precision for financial calculations
- **Commission tracking**: Both percentage and fixed commission support
- **Balance automation**: Real-time balance updates with each transaction
- **Cash reconciliation**: Physical count verification with discrepancy detection

### Reporting & Analytics
- **Shift reports**: Comprehensive end-of-shift summaries
- **Category analytics**: Income breakdown by business area
- **Payment analysis**: Performance by payment method
- **Historical tracking**: Complete transaction and session history

### Data Integrity
- **Audit trails**: Complete tracking of all financial operations
- **User attribution**: Every transaction linked to creating user
- **Timestamp tracking**: Created/updated timestamps on all records
- **Validation**: Form and model-level validation for data integrity

## Planned Modules (Future Development)

### 1. Papelería (Stationery) Module
**Status**: 🔄 Planned
**Purpose**: Handle stationery sales with inventory management
**Integration**: Will use existing transaction categories and reporting system

### 2. Bank Operations Module
**Status**: 🔄 Planned
**Purpose**: Handle banking transactions and transfers
**Integration**: Will leverage existing Entity and Bank models

### 3. Inventory Management
**Status**: 🔄 Planned
**Purpose**: Track stationery inventory, stock levels, and reorders

## Environment Configuration

### Required Environment Variables (.env)
```bash
# Database
DB_NAME=softwaretienda
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional
TIME_ZONE=America/Bogota
LANGUAGE_CODE=es-co
```

### Key Dependencies (requirements.txt)
- Django 5.2.6
- psycopg2-binary (PostgreSQL adapter)
- python-decouple (environment management)
- django-crispy-forms + crispy-bootstrap5 (form rendering)
- Pillow (image handling)
- gunicorn + whitenoise (production deployment)

## Development Guidelines

### Code Standards
- Follow Django best practices
- Use role-based access control consistently
- Maintain comprehensive audit trails
- Implement proper form validation
- Use Bootstrap 5 for consistent UI
- Add meaningful error messages and user feedback

### Security Practices
- Never expose secrets in code
- Use environment variables for configuration
- Implement proper permission checking
- Validate all user inputs
- Maintain audit trails for financial operations

### Testing Strategy
- Test role-based access control
- Validate financial calculations
- Test cash reconciliation logic
- Verify transaction integrity
- Test closing report generation

## Current System Capabilities

### Multi-User Support
- ✅ Role-based user management
- ✅ Individual user transaction tracking
- ✅ Session management per user
- ✅ Admin oversight and control

### Financial Operations
- ✅ Complete cash register lifecycle
- ✅ Income and expense tracking
- ✅ Commission management
- ✅ Multi-payment method support
- ✅ Real-time balance calculation
- ✅ Cash reconciliation with physical counts

### Reporting & Analytics
- ✅ Comprehensive shift reports
- ✅ Category-based income analysis
- ✅ Payment method breakdowns
- ✅ Discrepancy detection and reporting
- ✅ Historical data preservation
- ✅ Print-ready professional reports

### Business Intelligence Ready
- ✅ Transaction categorization for future modules
- ✅ Entity management for bank operations
- ✅ Extensible model structure
- ✅ Comprehensive audit trails
- ✅ Performance metrics tracking

## Next Development Steps

1. **Papelería Module Development**
   - Product catalog management
   - Inventory tracking
   - Sales integration with existing transaction system
   - Automatic category assignment for stationery sales

2. **Enhanced Reporting**
   - Weekly/monthly reports
   - User performance analytics
   - Inventory reports (when papelería is implemented)
   - Financial trend analysis

3. **Advanced Features**
   - CSV export functionality
   - Advanced filtering and search
   - Mobile app considerations
   - Integration with external payment systems

## Technical Notes

### Database Migrations Status
- ✅ Initial accounts migration (0001_initial.py)
- ✅ Initial caja migration (0001_initial.py)
- ✅ Enhanced caja migration (0002_transaction_category_cashregisterreport.py)

### Current Deployment State
- Development environment ready
- PostgreSQL database configured
- All models migrated and functional
- Admin interface configured
- User authentication fully operational
- Cash register system fully functional

---

**Last Updated**: December 2024
**Django Version**: 5.2.6
**Python Version**: 3.11+
**Database**: PostgreSQL
**Status**: Core POS functionality complete, ready for module expansion