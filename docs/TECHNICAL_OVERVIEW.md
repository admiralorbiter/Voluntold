# Technical Overview: Voluntold Architecture

## 🏗️ **System Architecture**

### **High-Level Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Salesforce    │    │   Voluntold     │    │   Website       │
│   (Data Source) │◄──►│   (Microservice)│◄──►│   (Frontend)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              ▲
                              │
                    ┌─────────────────┐
                    │  Google Sheets  │
                    │ (Virtual Events)│
                    └─────────────────┘
```

### **Technology Stack**
- **Backend**: Flask (Python)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML/CSS/JavaScript (Bootstrap)
- **Hosting**: PythonAnywhere
- **Integration**: Salesforce API (simple-salesforce), Google Sheets CSV
- **Authentication**: Flask-Login

## 🔄 **Data Flow**

### **1. Salesforce Sync Process**
```
Salesforce API Query
├── Query: SELECT * FROM Session__c WHERE Start_Date__c > TODAY
├── Frequency: Every 60 minutes (automated)
├── Manual: Dashboard "Sync Events" button
└── Result: JSON data with event information
```

### **2. Virtual Events Import Process**
```
Google Sheets (Public CSV)
├── URL: https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv
├── Fallback: https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0
├── Frequency: Manual import via dashboard
├── Processing: Skip first 3 rows, filter by Session Link and Presenter status
└── Result: Virtual events stored in same UpcomingEvent table
```

### **3. Data Processing Pipeline**
```
Raw Data → Validation → Transformation → Database Storage → API → Frontend
```

## 🗄️ **Database Schema**

### **Core Tables**

#### **upcoming_events**
Primary table storing all event data (Salesforce + Virtual)

**Salesforce Event Fields:**
- `id` (Primary Key)
- `salesforce_id` (Unique Salesforce ID)
- `name` (Event title)
- `available_slots` (Number of volunteer slots)
- `filled_volunteer_jobs` (Filled slots count)
- `date_and_time` (Formatted date/time string)
- `event_type` (Type of event)
- `registration_link` (Signup URL)
- `display_on_website` (Visibility toggle)
- `start_date` (DateTime for sorting)
- `status` (active/archived)
- `note` (Admin notes)

**Virtual Event Fields:**
- `source` (salesforce/virtual)
- `spreadsheet_id` (Google Sheet ID)
- `presenter_name` (Presenter name)
- `presenter_organization` (Presenter organization)
- `presenter_location` (Local/Not local)
- `topic_theme` (Event topic/theme)
- `teacher_name` (Contact teacher)
- `school_name` (School name)
- `school_level` (Elementary/High/etc)
- `district` (School district)

#### **event_district_mapping**
Links events to districts for display filtering
- `id` (Primary Key)
- `event_id` (Foreign Key to upcoming_events)
- `district` (District name)

#### **users**
Admin user management
- `id` (Primary Key)
- `username` (Login username)
- `password_hash` (Hashed password)
- `is_admin` (Admin flag)

## 🛠️ **Core Components**

### **Models** (`models/`)
- **`upcoming_event.py`**: Main event model with Salesforce + Virtual support
- **`event_district_mapping.py`**: District association model
- **`user.py`**: User authentication model

### **Services** (`services/`)
- **`google_sheets_service.py`**: Google Sheets CSV reader with robust column cleaning
- **Salesforce integration**: Direct API calls (no separate service)

### **Routes** (`routes/`)
- **`main.py`**: Public pages (login, signup)
- **`dashboard.py`**: Admin dashboard and virtual events dashboard
- **`upcoming_events.py`**: Event management and volunteer signup
- **`virtual_events.py`**: Virtual events API endpoints
- **`api.py`**: General API endpoints
- **`auth.py`**: Authentication routes
- **`sync.py`**: Salesforce sync functionality
- **`district.py`**: District management
- **`school_mappings.py`**: School mapping utilities
- **`dia.py`**: DIA-specific event handling

### **Templates** (`templates/`)
- **`base.html`**: Main layout template
- **`dashboard.html`**: Admin dashboard
- **`virtual_events_dashboard.html`**: Virtual events management
- **`signup.html`**: Volunteer signup page
- **`login.html`**: Admin login
- **`districts/`**: District-specific templates

## 🌐 **API Endpoints**

### **Event Management**
- `POST /sync_upcoming_events` - Manual sync trigger
- `GET /volunteer_signup_api` - Public event data
- `GET /api/events/archive` - Archived events
- `POST /toggle-event-visibility` - Toggle event display

### **District Management**
- `POST /events/api/events/<id>/districts` - Add district to event
- `DELETE /events/api/events/<id>/districts/<district>` - Remove district
- `GET /api/districts/search` - Search districts

### **Notes Management**
- `PUT /api/events/<id>/note` - Update event note
- `DELETE /api/events/<id>/note` - Delete event note

### **Virtual Events Management**
- `GET /api/virtual-events` - List all virtual events
- `POST /api/virtual-events/import` - Import from Google Sheets
- `GET /api/virtual-events/<id>` - Get specific virtual event
- `POST /api/virtual-events/<id>/toggle-visibility` - Toggle visibility
- `GET /api/virtual-events/sheet-info` - Get sheet information

## 🔒 **Security & Authentication**

### **Authentication**
- Flask-Login for session management
- Password hashing with Werkzeug
- Session cookies with SameSite protection

### **Authorization**
- Admin-only access to dashboard
- Public access to volunteer signup page
- API endpoints require authentication

### **Data Protection**
- SQL injection protection via SQLAlchemy ORM
- XSS protection via template escaping
- CSRF protection on forms

## ⚡ **Performance Considerations**

### **Database Optimization**
- Indexed fields: `start_date`, `source`, `status`
- Efficient queries with proper joins
- Pagination for large result sets

### **API Performance**
- JSON responses for fast data transfer
- Minimal database queries per request
- Caching for frequently accessed data

### **Monitoring & Logging**
- Application logging for debugging
- Error tracking and reporting
- API usage monitoring

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=sqlite:///instance/your_database.db

# Salesforce Integration
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token
SALESFORCE_DOMAIN=login.salesforce.com

# Virtual Events
VIRTUAL_EVENTS_SHEET_ID=your_google_sheet_id

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_ENV=development
```

### **Google Sheets Integration**
- **Public CSV Export**: No authentication required
- **Primary URL**: `https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv`
- **Fallback URL**: `https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0`
- **Data Processing**: Skip first 3 rows, robust column name cleaning

## 🚀 **Deployment**

### **PythonAnywhere Setup**
1. Upload code to PythonAnywhere
2. Configure environment variables
3. Set up scheduled tasks for Salesforce sync
4. Configure web app with Flask

### **Database Migration**
```python
# Run migrations for new fields
from models import db
db.create_all()
```

### **Monitoring**
- Check logs for sync errors
- Monitor Salesforce API connectivity
- Verify Google Sheets accessibility
- API endpoint health checks

## 🔄 **Sync Processes**

### **Salesforce Sync**
- **Automated**: Every 60 minutes via scheduled task
- **Manual**: Dashboard "Sync Events" button
- **Process**: Query → Validate → Transform → Store → Archive

### **Virtual Events Import**
- **Manual**: Dashboard "Import Virtual Events" button
- **Process**: CSV Download → Parse → Filter → Store → Update

## 📊 **Data Validation**

### **Salesforce Events**
- Required fields validation
- Date format validation
- URL validation for registration links
- Slot count validation

### **Virtual Events**
- Session Link presence validation
- Date/time parsing validation
- Presenter status filtering
- Column structure validation

## 🛡️ **Error Handling**

### **API Error Responses**
- Consistent JSON error format
- Appropriate HTTP status codes
- Detailed error messages for debugging
- Graceful fallbacks for external services

### **Database Error Handling**
- Transaction rollback on errors
- Connection retry logic
- Data integrity constraints

## 📈 **Scalability Considerations**

### **Current Limitations**
- SQLite for development (single connection)
- Manual virtual events import
- Single-threaded Flask app

### **Future Improvements**
- PostgreSQL for production
- Automated virtual events sync
- API rate limiting
- Caching layer implementation

## 🔍 **Debugging & Troubleshooting**

### **Common Issues**
- Salesforce API connectivity
- Google Sheets access permissions
- Database migration errors
- API endpoint authentication

### **Debug Tools**
- Flask debug mode
- Application logging
- API endpoint testing
- Database query inspection

