# Project Structure & Organization

## 📁 **Directory Layout**

```
Voluntold/
├── 📁 docs/                    # Documentation and project tracking
│   ├── DEVELOPMENT_STATUS.md   # Current development progress
│   └── PROJECT_STRUCTURE.md   # This file
├── 📁 scripts/                 # Utility and setup scripts
│   ├── create_admin.py        # Create admin user
│   ├── create_jonlane.py     # Create additional user
│   ├── create_test_data.py   # Populate test database
│   └── test_archive_functionality.py  # Test archive logic
├── 📁 tests/                   # Automated test suite
│   ├── conftest.py           # Test configuration
│   └── test_models.py        # Model tests
├── 📁 models/                  # Database models
│   ├── __init__.py
│   ├── upcoming_event.py     # Event model with archive logic
│   ├── school_mapping.py     # School-to-district mappings
│   ├── event_district_mapping.py  # Event-district relationships
│   └── user.py               # User authentication
├── 📁 routes/                  # Flask route handlers
│   ├── __init__.py
│   ├── api.py                # API endpoints
│   ├── auth.py               # Authentication routes
│   ├── dashboard.py          # Admin dashboard
│   ├── main.py               # Main public routes
│   ├── upcoming_events.py    # Event management & sync
│   └── school_mappings.py    # District management
├── 📁 templates/               # HTML templates
│   ├── base.html             # Base template
│   ├── dashboard.html        # Admin dashboard
│   └── index.html            # Public volunteer page
├── 📁 static/                  # Static assets
│   └── css/                  # Stylesheets
├── 📁 data/                    # Data files
│   └── school-mappings.csv   # District mapping data
├── 📁 migrations/              # Database migrations
├── 📁 logs/                    # Application logs
├── 📁 services/                # Business logic services
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview
```

## 🔧 **Scripts Directory**

The `scripts/` folder contains utility scripts for:

### **Setup & Administration**
- `create_admin.py` - Create the initial admin user
- `create_jonlane.py` - Create additional user accounts

### **Testing & Development**
- `create_test_data.py` - Populate database with sample events for testing
- `test_archive_functionality.py` - Test the archive system logic

### **Usage Examples**
```bash
# Create admin user
python scripts/create_admin.py

# Set up test data
python scripts/create_test_data.py

# Test archive functionality
python scripts/test_archive_functionality.py
```

## 📚 **Documentation Directory**

The `docs/` folder contains:

- **`DEVELOPMENT_STATUS.md`** - Current sprint progress and next priorities
- **`PROJECT_STRUCTURE.md`** - This file explaining the codebase organization

## 🧪 **Testing Directory**

The `tests/` folder contains:

- **`conftest.py`** - Test configuration and fixtures
- **`test_models.py`** - Unit tests for database models

## 📊 **Data Directory**

The `data/` folder contains:

- **`school-mappings.csv`** - Static mapping of schools to districts

## 🚀 **Key Files**

### **Application Entry Points**
- **`app.py`** - Main Flask application setup
- **`sync_script.py`** - Automated Salesforce sync script

### **Configuration**
- **`config.py`** - Application configuration
- **`.env`** - Environment variables (not in repo)

### **Dependencies**
- **`requirements.txt`** - Python package dependencies

## 🔄 **Development Workflow**

1. **Scripts** → Use utility scripts for setup and testing
2. **Models** → Define database structure and business logic
3. **Routes** → Handle HTTP requests and responses
4. **Templates** → Render user interface
5. **Tests** → Verify functionality works correctly
6. **Docs** → Track progress and document decisions

## 📝 **Adding New Files**

When adding new files, follow these conventions:

- **Utility scripts** → `scripts/` folder
- **Documentation** → `docs/` folder
- **Tests** → `tests/` folder
- **Models** → `models/` folder
- **Routes** → `routes/` folder
- **Templates** → `templates/` folder
- **Static assets** → `static/` folder

## 🎯 **Current Organization Status**

- ✅ **Scripts organized** in `scripts/` folder
- ✅ **Documentation organized** in `docs/` folder
- ✅ **Tests organized** in `tests/` folder
- ✅ **Core application** remains in root for easy access
- ✅ **Clear separation** between utilities and application code
