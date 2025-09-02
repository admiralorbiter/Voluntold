# Technical Overview: Voluntold Architecture

## 🏗️ **System Architecture**

### **High-Level Overview**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Salesforce    │    │   Voluntold     │    │   Website       │
│   (Data Source) │◄──►│   (Microservice)│◄──►│   (Frontend)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**
- **Backend**: Flask (Python)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML/CSS/JavaScript (Bootstrap)
- **Hosting**: PythonAnywhere
- **Integration**: Salesforce API (simple-salesforce)
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

### **2. Data Processing**
```
Raw Salesforce Data
├── Parse event information
├── Update existing events
├── Add new events
├── Archive full events (0 slots)
├── Delete past events
└── Preserve staff configurations
```

### **3. Website Integration**
```
Event Data
├── Volunteer Signup Page: Active events with display_on_website = true
├── District Pages: Events linked to specific districts
├── DIA Page: Events with event_type = 'DIA'
└── Admin Dashboard: All events with management controls
```

## 🗄️ **Database Schema**

### **Core Tables**

#### **UpcomingEvent**
```sql
CREATE TABLE upcoming_events (
    id INTEGER PRIMARY KEY,
    salesforce_id VARCHAR(18) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    available_slots INTEGER,
    filled_volunteer_jobs INTEGER,
    date_and_time VARCHAR(100),
    event_type VARCHAR(50),
    registration_link TEXT,
    display_on_website BOOLEAN DEFAULT FALSE,
    start_date DATETIME,
    status VARCHAR(20) DEFAULT 'active',
    note TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

#### **SchoolMapping**
```sql
CREATE TABLE school_mappings (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(255) NOT NULL,
    parent_salesforce_id VARCHAR(255) NOT NULL
);
```

#### **EventDistrictMapping**
```sql
CREATE TABLE event_district_mappings (
    id INTEGER PRIMARY KEY,
    event_id INTEGER REFERENCES upcoming_events(id),
    district VARCHAR(255) NOT NULL
);
```

#### **User**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    security_level INTEGER DEFAULT 0
);
```

## 🔧 **Key Components**

### **Models** (`models/`)
- **`upcoming_event.py`**: Core event model with archive logic
- **`school_mapping.py`**: School-to-district mappings
- **`event_district_mapping.py`**: Event-district relationships
- **`user.py`**: Admin authentication

### **Routes** (`routes/`)
- **`upcoming_events.py`**: Event sync and management
- **`dashboard.py`**: Admin dashboard functionality
- **`auth.py`**: User authentication
- **`api.py`**: API endpoints
- **`main.py`**: Public routes

### **Templates** (`templates/`)
- **`dashboard.html`**: Admin interface
- **`signup.html`**: Volunteer signup page
- **`base.html`**: Base template
- **`login.html`**: Authentication

### **Static Assets** (`static/`)
- **`css/dashboard.css`**: Dashboard styling
- **`css/style.css`**: General styling
- **JavaScript**: Inline in templates

## 🔄 **Sync Process Details**

### **Automated Sync (Every 60 Minutes)**
```python
def sync_upcoming_events():
    # 1. Archive full events
    archived_count = UpcomingEvent.query.filter(
        UpcomingEvent.available_slots <= 0
    ).update({'status': 'archived'})
    
    # 2. Delete past events
    deleted_count = UpcomingEvent.query.filter(
        UpcomingEvent.start_date < yesterday
    ).delete()
    
    # 3. Query Salesforce
    sf = Salesforce(username, password, security_token)
    events = sf.query("SELECT * FROM Session__c WHERE Start_Date__c > TODAY")
    
    # 4. Update database
    new_count, updated_count = UpcomingEvent.upsert_from_salesforce(events)
    
    return {
        'success': True,
        'new_count': new_count,
        'updated_count': updated_count,
        'deleted_count': deleted_count,
        'archived_count': archived_count
    }
```

### **Archive System Logic**
```python
# Archive full events
if event.available_slots <= 0:
    event.status = 'archived'
    # Preserve all staff settings (districts, notes, visibility)

# Reactivate when slots become available
if event.status == 'archived' and event.available_slots > 0:
    event.status = 'active'
    # All previous settings are automatically restored
```

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
- Input validation on all forms
- SQL injection prevention via SQLAlchemy ORM
- XSS protection via template escaping

## 🚀 **Deployment**

### **PythonAnywhere Configuration**
- **Web App**: Flask application
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Static Files**: Served from `/static/`
- **Logs**: Rotating file handler in `logs/`

### **Environment Variables**
```bash
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql://... (production)
```

### **Automated Tasks**
- **Hourly Sync**: Scheduled task in PythonAnywhere
- **Log Rotation**: Automatic log file management
- **Database Backups**: Regular backup schedule

## 📊 **Performance Considerations**

### **Database Optimization**
- Indexes on frequently queried fields
- Efficient queries with proper joins
- Connection pooling for production

### **API Performance**
- Pagination for large event lists
- Caching for district data
- Efficient JSON serialization

### **Sync Performance**
- Batch processing for large datasets
- Error handling and retry logic
- Progress reporting for manual syncs

## 🔍 **Monitoring & Logging**

### **Application Logs**
- Sync process logging
- Error tracking
- Performance metrics

### **User Activity**
- Login/logout tracking
- Event modification history
- API usage monitoring

### **System Health**
- Database connection status
- Salesforce API connectivity
- Sync success/failure rates

## 🧪 **Testing Strategy**

### **Unit Tests**
- Model validation
- Business logic
- API endpoints

### **Integration Tests**
- Salesforce sync process
- Database operations
- User workflows

### **Manual Testing**
- Dashboard functionality
- Event management
- Archive system

## 🔮 **Future Technical Improvements**

### **Immediate**
- Comprehensive test coverage
- Better error handling
- Input validation improvements

### **Short Term**
- Real-time updates via WebSockets
- Advanced caching
- API rate limiting

### **Long Term**
- Microservices architecture
- Event sourcing
- Advanced analytics

---

**Key Takeaway**: The system is built on solid foundations with Flask and SQLAlchemy, providing a robust platform for event management with room for growth and improvement.
