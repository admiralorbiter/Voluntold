# Quick Reference Guide

## 🎯 **What This System Does**

**Voluntold** is a microservice for PREP-KC that manages volunteer recruitment events. It connects Salesforce event data and Google Sheets virtual events to website pages, allowing staff to control which events appear where and how they're displayed to volunteers.

## 🚀 **Getting Started**

### **Setup Commands**
```bash
# Install dependencies
pip install -r requirements.txt

# Create admin user
python scripts/create_admin.py

# Set up test data
python scripts/create_test_data.py

# Run the app
python app.py
```

### **Testing Commands**
```bash
# Test archive functionality
python scripts/test_archive_functionality.py

# Run automated tests
python -m pytest tests/
```

## 📁 **Where to Find Things**

### **Documentation**
- **`docs/BUSINESS_OVERVIEW.md`** - What PREP-KC does and why this system exists
- **`docs/USER_WORKFLOW.md`** - How staff currently manage events
- **`docs/TECHNICAL_OVERVIEW.md`** - System architecture and technical details
- **`docs/DEVELOPMENT_STATUS.md`** - Current progress and next steps
- **`docs/ARCHIVE_SYSTEM.md`** - How archive system works
- **`docs/PROJECT_STRUCTURE.md`** - Codebase organization

### **Scripts & Utilities**
- **`scripts/create_admin.py`** - Create admin users
- **`scripts/create_test_data.py`** - Populate test database
- **`scripts/test_archive_functionality.py`** - Test archive system

### **Key Application Files**
- **`app.py`** - Main Flask application
- **`routes/upcoming_events.py`** - Event sync and management
- **`routes/virtual_events.py`** - Virtual events API and import
- **`models/upcoming_event.py`** - Event model with archive logic
- **`templates/dashboard.html`** - Admin dashboard
- **`templates/virtual_events_dashboard.html`** - Virtual events management

## 🎯 **Current Workflow (PREP-KC Staff)**

### **Salesforce Event Management Process**
1. **Create event in Salesforce** → Event appears in dashboard after sync
2. **Manually link to districts** → Event appears on district pages
3. **Toggle visibility ON** → Event appears on volunteer signup page
4. **Add notes for volunteers** → Notes display on event details
5. **Monitor event status** → Handle changes as needed

### **Virtual Events Management Process**
1. **Update Google Sheet** → Virtual events data ready for import
2. **Import from dashboard** → Events appear in virtual events dashboard
3. **Toggle visibility** → Control which virtual events show on website
4. **Filter and search** → Find specific virtual events easily

### **Current Pain Point: Manual District Linking**
- Staff must manually link every event to districts
- Time-consuming: 2-3 minutes per event
- Error-prone: ~5% manual linking errors
- **Next Priority**: Automatic district linking system

## 🔄 **Archive System Quick Facts**

### **What Happens When Events Fill Up**
1. Event status changes from `'active'` → `'archived'`
2. Event disappears from volunteer signup page
3. **All staff settings are preserved** (districts, notes, visibility)

### **What Happens When People Drop Out**
1. During next sync, if `available_slots > 0`
2. Event status automatically changes from `'archived'` → `'active'`
3. Event reappears on volunteer signup page
4. **All previous settings are restored automatically**

### **Dashboard Views**
- **Active Events**: Events currently accepting volunteers
- **Archived Events**: Full events (0 available slots)
- **Virtual Events**: Google Sheets imported events
- **Toggle Button**: Switch between views

## 🎯 **Virtual Events System**

### **Google Sheets Integration**
- **Sheet ID**: Configured via `VIRTUAL_EVENTS_SHEET_ID` environment variable
- **Import Process**: Manual import via dashboard button
- **Data Filtering**: Only imports events with Session Link and no Presenter
- **Display**: Shows date, time, title, topic, district, and registration link

### **Virtual Events Dashboard**
- **Route**: `/virtual-events`
- **Features**: Import, filter, search, toggle visibility
- **Filters**: Search, status, date range, custom date range
- **Management**: Toggle individual event visibility

### **Virtual Events API**
- `GET /api/virtual-events` - List all virtual events
- `POST /api/virtual-events/import` - Import from Google Sheets
- `GET /api/virtual-events/<id>` - Get specific virtual event
- `POST /api/virtual-events/<id>/toggle-visibility` - Toggle visibility
- `GET /api/virtual-events/sheet-info` - Get sheet information

## 🧪 **Testing Scenarios**

### **Test Archive Functionality**
```bash
# Run the archive test script
python scripts/test_archive_functionality.py

# Expected output:
# ✅ Archive system working correctly
# ✅ Events properly archived when full
# ✅ Events restored when slots available
```

### **Test Virtual Events Import**
1. Go to `/virtual-events` dashboard
2. Click "Import Virtual Events" button
3. Check import results and event display
4. Test filtering and search functionality

## 🔧 **Common Tasks**

### **Add New Admin User**
```bash
python scripts/create_admin.py
# Follow prompts to create username/password
```

### **Sync Salesforce Events**
1. Go to main dashboard
2. Click "Sync Events" button
3. Check sync results in status message

### **Import Virtual Events**
1. Go to `/virtual-events` dashboard
2. Click "Import Virtual Events" button
3. Review imported events and toggle visibility as needed

### **Add New API Endpoints**
1. Create route in appropriate `routes/` file
2. Add authentication with `@login_required`
3. Test endpoint functionality
4. Update API documentation

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Events Not Syncing**
- Check Salesforce credentials in environment variables
- Verify Salesforce API permissions
- Check application logs for sync errors

#### **Virtual Events Import Failing**
- Verify `VIRTUAL_EVENTS_SHEET_ID` is set correctly
- Check Google Sheet is public and accessible
- Review import error messages in dashboard

#### **Dashboard Not Loading**
- Check database connection
- Verify all environment variables are set
- Check Flask application logs

#### **Authentication Issues**
- Verify user exists in database
- Check password hashing
- Clear browser cookies and try again

### **Debug Commands**
```bash
# Check database
python -c "from app import app; from models import db; app.app_context().push(); print('DB OK')"

# Test Salesforce connection
python -c "from services.salesforce_service import SalesforceService; print('SF OK')"

# Test Google Sheets access
python -c "from services.google_sheets_service import GoogleSheetsService; print('GS OK')"
```

## 📊 **Database Schema Quick Reference**

### **upcoming_events Table**
- **Salesforce Events**: `source='salesforce'`, `salesforce_id` populated
- **Virtual Events**: `source='virtual'`, `spreadsheet_id` populated
- **Common Fields**: `name`, `date_and_time`, `registration_link`, `display_on_website`
- **Virtual-Specific**: `presenter_name`, `topic_theme`, `district`, `school_name`

### **Key Relationships**
- `event_district_mapping` → Links events to districts
- `users` → Admin user management

## 🔄 **Environment Variables**

### **Required Variables**
```bash
# Database
DATABASE_URL=sqlite:///instance/your_database.db

# Salesforce
SALESFORCE_USERNAME=your_username
SALESFORCE_PASSWORD=your_password
SALESFORCE_SECURITY_TOKEN=your_token

# Virtual Events
VIRTUAL_EVENTS_SHEET_ID=your_google_sheet_id

# Flask
SECRET_KEY=your_secret_key
```

## 📈 **Performance Tips**

### **Database Optimization**
- Use indexed fields for queries (`start_date`, `source`, `status`)
- Limit result sets with pagination
- Use efficient joins for related data

### **API Optimization**
- Use JSON responses for fast data transfer
- Minimize database queries per request
- Implement proper error handling

### **Frontend Optimization**
- Use `async/await` for API calls
- Implement client-side filtering for large datasets
- Cache frequently accessed data

## 🎯 **Next Development Priorities**

1. **Automatic District Linking** - Reduce manual work
2. **Unified Event API** - Include virtual events in main API
3. **Advanced Filtering** - More sophisticated search options
4. **Bulk Operations** - Mass update capabilities
5. **Analytics Dashboard** - Event performance metrics