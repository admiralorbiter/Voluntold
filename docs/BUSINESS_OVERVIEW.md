# Business Overview: PREP-KC Event Management System

## 🎯 **What This System Does**

**Voluntold** is a microservice that manages volunteer recruitment events for PREP-KC, a non-profit organization. The system connects Salesforce event data to website pages, allowing staff to control which events appear where and how they're displayed to potential volunteers.

## 🏢 **About PREP-KC**

- **Organization**: Non-profit focused on education and community engagement
- **Mission**: Recruit volunteers for school events and career fairs
- **Users**: Staff members who manage event visibility and volunteer recruitment
- **End Users**: Volunteers who sign up for events through the website

## 🔄 **Current Workflow**

### **1. Event Creation in Salesforce**
```
Staff creates event in Salesforce
↓
Event includes: name, date, available slots, event type, etc.
↓
Salesforce data is consistent and well-structured
```

### **2. Automatic Sync Process**
```
Every 60 minutes (or manual sync)
↓
System pulls all future events from Salesforce
↓
Events appear in admin dashboard
```

### **3. Manual District Linking (Current Pain Point)**
```
Staff must manually link each event to districts
↓
This determines which district page the event appears on
↓
Process is time-consuming and error-prone
```

### **4. Event Visibility Control**
```
Staff toggles events on/off for website display
↓
Toggle controls whether event appears on volunteer signup page
↓
DIA events automatically appear on DIA page
```

## 📱 **Website Pages & Event Display**

### **Public Pages (Volunteer-Facing)**
- **Volunteer Signup Page** (`/volunteer_signup`): Shows all active events with `display_on_website = true`
- **District Pages**: Show events linked to specific districts
- **DIA Events Page**: Automatically shows all DIA-type events

### **Admin Pages (Staff-Facing)**
- **Dashboard** (`/dashboard`): Manage all events, visibility, districts, and notes
- **Archive View**: View full events that are no longer accepting volunteers

## 🎯 **Current Pain Points**

### **1. Manual District Linking**
- **Problem**: Staff must manually link every event to districts
- **Impact**: Time-consuming, error-prone, doesn't scale
- **Why**: Can't be done in Salesforce directly
- **Solution Needed**: Automatic district linking based on event data

### **2. Event Management Overhead**
- **Problem**: Staff spend significant time on manual configuration
- **Impact**: Less time for actual volunteer recruitment
- **Solution Needed**: Automate routine tasks

## 🚀 **System Benefits**

### **For Staff**
- ✅ Centralized event management
- ✅ Control over event visibility
- ✅ Preserved settings when events fill up (archive system)
- ✅ Easy district linking interface
- ✅ Event notes for volunteers

### **For Volunteers**
- ✅ Clear event information
- ✅ Easy signup process
- ✅ District-specific event views
- ✅ Real-time availability

## 📊 **Event Types & Display Logic**

### **Event Types**
- **Career Fairs**: General volunteer events
- **DIA Events**: Automatically appear on DIA page
- **Other Types**: Custom event categories

### **Display Rules**
1. **Volunteer Signup Page**: `display_on_website = true` AND `status = 'active'`
2. **District Pages**: Event must be linked to that district
3. **DIA Page**: Event type must be "DIA" (automatic)
4. **Archived Events**: `status = 'archived'` (full events, 0 available slots)

## 🔧 **Technical Environment**

### **Hosting**
- **Platform**: PythonAnywhere
- **Database**: SQLite (development) / PostgreSQL (production)
- **Sync**: Automated every 60 minutes

### **Integrations**
- **Salesforce**: Primary data source via API
- **Website**: Multiple pages consume event data
- **Admin Interface**: Flask-based dashboard

## 📈 **Success Metrics**

### **Current Goals**
- Reduce manual district linking time by 80%
- Maintain 100% data accuracy
- Keep sync process under 30 seconds
- Zero data loss during event status changes

### **Future Goals**
- 90%+ automatic district matching accuracy
- Real-time event updates
- Advanced filtering and search
- Bulk operations for staff efficiency

## 🎯 **Next Priority: Automatic District Linking**

### **The Problem**
Staff currently spend significant time manually linking events to districts because:
1. Salesforce doesn't have district linking functionality
2. Event names don't always clearly indicate district
3. Some events span multiple districts
4. Manual process is error-prone and doesn't scale

### **The Solution**
Build an automatic district linking system that:
1. Analyzes event names for district keywords
2. Uses school-to-district mappings from `data/school-mappings.csv`
3. Provides confidence scores for automatic assignments
4. Allows manual override for edge cases
5. Reduces staff workload while maintaining accuracy

---

**Key Takeaway**: This system bridges the gap between Salesforce event management and website display, giving PREP-KC staff control over volunteer recruitment while automating routine tasks.
