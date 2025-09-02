# Quick Reference Guide

## 🎯 **What This System Does**

**Voluntold** is a microservice for PREP-KC that manages volunteer recruitment events. It connects Salesforce event data to website pages, allowing staff to control which events appear where and how they're displayed to volunteers.

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
- **`models/upcoming_event.py`** - Event model with archive logic
- **`templates/dashboard.html`** - Admin dashboard

## 🎯 **Current Workflow (PREP-KC Staff)**

### **Event Management Process**
1. **Create event in Salesforce** → Event appears in dashboard after sync
2. **Manually link to districts** → Event appears on district pages
3. **Toggle visibility ON** → Event appears on volunteer signup page
4. **Add notes for volunteers** → Notes display on event details
5. **Monitor event status** → Handle changes as needed

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
- **Toggle Button**: Switch between views

## 🧪 **Testing Scenarios**

### **Test Archive Functionality**
```bash
python scripts/create_test_data.py
python scripts/test_archive_functionality.py
```

### **Manual Testing Steps**
1. Go to `/dashboard`
2. Click "Show Archived" to see archived events
3. Click "Show Active" to return to active events
4. Test event visibility toggles
5. Test district linking and notes

## 🔧 **Common Development Tasks**

### **Add New Event Fields**
1. Update `models/upcoming_event.py`
2. Update sync logic in `routes/upcoming_events.py`
3. Update dashboard template in `templates/dashboard.html`
4. Update test data in `scripts/create_test_data.py`

### **Add New API Endpoints**
1. Add route in appropriate `routes/` file
2. Update dashboard JavaScript if needed
3. Add tests in `tests/` folder

### **Database Changes**
1. Update model in `models/` folder
2. Create migration in `migrations/` folder
3. Update test data scripts

## 📊 **Key Data Models**

### **UpcomingEvent**
- `status`: 'active' or 'archived'
- `available_slots`: Number of volunteer slots
- `display_on_website`: Visibility toggle
- `note`: Staff notes for volunteers

### **EventDistrictMapping**
- Links events to districts (many-to-many)
- Preserved during archive/reactivation cycles

### **SchoolMapping**
- Static mapping of schools to districts
- Used for automatic district linking (future feature)

## 🚨 **Troubleshooting**

### **Archive View Not Working**
- Check browser console for JavaScript errors
- Verify `/api/events/archive` endpoint returns data
- Check that events have `status = 'archived'`

### **Events Not Syncing**
- Check Salesforce credentials in `.env`
- Verify Salesforce API permissions
- Check sync logs in terminal

### **Dashboard Issues**
- Check browser console for errors
- Verify all JavaScript functions are defined
- Check that event data includes `status` field

## 📝 **Code Style & Conventions**

### **File Organization**
- **Scripts** → `scripts/` folder
- **Documentation** → `docs/` folder
- **Tests** → `tests/` folder
- **Models** → `models/` folder
- **Routes** → `routes/` folder

### **JavaScript**
- Use `async/await` for API calls
- Add console logging for debugging
- Handle errors gracefully with user feedback

### **Python**
- Use type hints where possible
- Add docstrings for complex functions
- Handle exceptions with meaningful messages

## 🎯 **Next Development Priority**

### **Automatic District Linking System**
- **Goal**: Automatically link events to districts based on event names
- **Approach**: Pattern matching + school-to-district mappings
- **Target**: 90%+ accuracy, reduce manual work by 80%
- **Status**: In planning phase

### **Implementation Plan**
1. **Analysis**: Study existing event names and district patterns
2. **Algorithm**: Create district matching logic with confidence scoring
3. **Integration**: Add to sync process with manual override capability
4. **Testing**: Validate with real event data

---

**Need Help?** 
- **Business Context**: See `docs/BUSINESS_OVERVIEW.md`
- **User Workflow**: See `docs/USER_WORKFLOW.md` 
- **Technical Details**: See `docs/TECHNICAL_OVERVIEW.md`
- **Debugging**: Check console logs and sync output
