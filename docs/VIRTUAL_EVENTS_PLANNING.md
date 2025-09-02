# Virtual Events Feature: Planning & Task Breakdown

## 🎯 **Feature Overview**

**Goal**: Add support for virtual events sourced from Google Spreadsheets, providing API access and database storage similar to Salesforce events.

**Business Value**: 
- Expand event types beyond in-person events
- Reduce manual data entry for virtual events
- Provide consistent API for all event types
- Maintain existing dashboard functionality

## 📋 **High-Level Requirements**

### **Core Functionality**
- [ ] Google Spreadsheet integration for virtual events
- [ ] Database storage for virtual event data
- [ ] API endpoints for virtual events
- [ ] Dashboard integration for virtual event management
- [ ] Sync process for spreadsheet updates

### **Data Requirements**
- [ ] Map spreadsheet columns to event fields
- [ ] Handle virtual event-specific fields
- [ ] Maintain data consistency with Salesforce events
- [ ] Support event status management (active/archived)

## 🏗️ **Technical Architecture**

### **Data Flow**
```
Google Spreadsheet (Public) → CSV Export → Import Process → Database → API → Dashboard/Website
```

### **Google Sheets Integration Approach**
Based on existing implementation, we'll use the **public CSV export method**:
- **Primary URL Format**: `https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv`
- **Fallback URL Format**: `https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0`
- **Dependencies**: `pandas` for CSV reading, `requests` for HTTP calls
- **Authentication**: None required (public spreadsheet)

### **Database Changes**
- [ ] Extend `UpcomingEvent` model for virtual events
- [ ] Add virtual event source tracking
- [ ] Maintain compatibility with existing events

### **New Components**
- [ ] Google Sheets CSV reader service
- [ ] Virtual event sync process
- [ ] Virtual event management routes
- [ ] Dashboard UI for virtual events

## 📊 **Task Breakdown by Priority**

### **Phase 1: Foundation & Planning** 🔴 **HIGH PRIORITY**

#### **1.1 Requirements Analysis**
- [ ] **Analyze existing event data structure**
  - [ ] Review `UpcomingEvent` model fields
  - [ ] Identify required vs optional fields
  - [ ] Document field mappings needed
- [ ] **Research Google Sheets API**
  - [ ] Review authentication methods
  - [ ] Understand data access patterns
  - [ ] Identify rate limits and constraints
- [ ] **Define virtual event data model**
  - [ ] Map spreadsheet columns to database fields
  - [ ] Identify virtual-specific fields needed
  - [ ] Plan data validation requirements

#### **1.2 Technical Setup**
- [ ] **Set up Google Sheets public access**
  - [ ] Create public Google Spreadsheet for virtual events
  - [ ] Configure spreadsheet with proper column headers
  - [ ] Test CSV export URL format
  - [ ] Document spreadsheet structure requirements
- [ ] **Install required dependencies**
  - [ ] Add `pandas` to requirements.txt (if not already present)
  - [ ] Add `requests` for HTTP calls (if not already present)
  - [ ] Update environment variables for spreadsheet ID

### **Phase 2: Database & Models** 🟡 **MEDIUM PRIORITY**

#### **2.1 Database Schema Updates**
- [ ] **Extend UpcomingEvent model**
  - [ ] Add `source` field (salesforce/virtual)
  - [ ] Add `spreadsheet_id` field for virtual events
  - [ ] Add `spreadsheet_url` field for reference
  - [ ] Add virtual event specific fields if needed
- [ ] **Create database migration**
  - [ ] Write migration script
  - [ ] Test migration on development database
  - [ ] Plan rollback strategy

#### **2.2 Model Updates**
- [ ] **Update UpcomingEvent model**
  - [ ] Add virtual event fields
  - [ ] Update validation logic
  - [ ] Add virtual event methods
- [ ] **Create VirtualEvent model (if needed)**
  - [ ] Define virtual-specific fields
  - [ ] Add relationship to UpcomingEvent
  - [ ] Implement virtual event logic

### **Phase 3: Google Sheets Integration** 🟡 **MEDIUM PRIORITY**

#### **3.1 Google Sheets Service**
- [ ] **Create Google Sheets CSV reader service**
  - [ ] Implement CSV URL construction (gviz/tq format)
  - [ ] Add fallback URL format (export?format=csv)
  - [ ] Add error handling and logging
  - [ ] Add retry logic for failed requests
- [ ] **Data mapping and validation**
  - [ ] Map spreadsheet columns to event fields
  - [ ] Implement data validation
  - [ ] Handle missing or invalid data
  - [ ] Add data transformation logic

#### **3.2 Import Process**
- [ ] **Create virtual event import function**
  - [ ] Read data from Google Sheets
  - [ ] Validate and transform data
  - [ ] Insert/update events in database
  - [ ] Handle import errors gracefully
- [ ] **Add import logging and monitoring**
  - [ ] Log import results
  - [ ] Track import statistics
  - [ ] Add error reporting

### **Phase 4: API Endpoints** 🟢 **LOW PRIORITY**

#### **4.1 Virtual Event API**
- [ ] **Create virtual event routes**
  - [ ] `GET /api/virtual-events` - List virtual events
  - [ ] `POST /api/virtual-events/import` - Import from spreadsheet
  - [ ] `GET /api/virtual-events/<id>` - Get specific virtual event
  - [ ] `PUT /api/virtual-events/<id>` - Update virtual event
- [ ] **Add API authentication**
  - [ ] Secure virtual event endpoints
  - [ ] Add rate limiting
  - [ ] Implement proper error responses

#### **4.2 Unified Event API**
- [ ] **Update existing event APIs**
  - [ ] Modify `/volunteer_signup_api` to include virtual events
  - [ ] Update event filtering to handle virtual events
  - [ ] Ensure backward compatibility

### **Phase 5: Dashboard Integration** 🟢 **LOW PRIORITY**

#### **5.1 Dashboard UI Updates**
- [ ] **Add virtual event management**
  - [ ] Virtual event import button
  - [ ] Virtual event status indicators
  - [ ] Virtual event filtering options
- [ ] **Update event display**
  - [ ] Show virtual event source
  - [ ] Add virtual event specific fields
  - [ ] Maintain existing functionality

#### **5.2 Admin Interface**
- [ ] **Add spreadsheet management**
  - [ ] Configure spreadsheet URL
  - [ ] Test spreadsheet connection
  - [ ] View import history
- [ ] **Add virtual event controls**
  - [ ] Toggle virtual event visibility
  - [ ] Manage virtual event notes
  - [ ] Handle virtual event districts

### **Phase 6: Testing & Validation** 🔴 **HIGH PRIORITY**

#### **6.1 Unit Testing**
- [ ] **Test Google Sheets CSV integration**
  - [ ] Test CSV URL construction
  - [ ] Test data reading from public sheets
  - [ ] Test error handling and fallback URLs
- [ ] **Test database operations**
  - [ ] Test model updates
  - [ ] Test data validation
  - [ ] Test migration scripts

#### **6.2 Integration Testing**
- [ ] **Test import process**
  - [ ] Test with sample spreadsheet
  - [ ] Test error scenarios
  - [ ] Test data consistency
- [ ] **Test API endpoints**
  - [ ] Test all virtual event endpoints
  - [ ] Test unified event API
  - [ ] Test authentication and authorization

#### **6.3 User Acceptance Testing**
- [ ] **Test dashboard functionality**
  - [ ] Test virtual event management
  - [ ] Test import process
  - [ ] Test event display
- [ ] **Test end-to-end workflow**
  - [ ] Create sample virtual events
  - [ ] Test import and display
  - [ ] Verify API functionality

## 🔧 **Implementation Strategy**

### **Incremental Development Approach**
1. **Start with Phase 1** - Foundation and planning
2. **Build Phase 2** - Database and models
3. **Implement Phase 3** - Google Sheets integration
4. **Add Phase 4** - API endpoints
5. **Complete Phase 5** - Dashboard integration
6. **Finish with Phase 6** - Testing and validation

### **Risk Mitigation**
- [ ] **Backup existing data** before database changes
- [ ] **Test in development environment** first
- [ ] **Implement feature flags** for gradual rollout
- [ ] **Maintain backward compatibility** throughout

### **Success Criteria**
- [ ] Virtual events can be imported from Google Sheets
- [ ] Virtual events appear in dashboard alongside Salesforce events
- [ ] API provides unified access to all event types
- [ ] No impact on existing functionality
- [ ] Import process is reliable and error-resistant

## 📅 **Estimated Timeline**

### **Phase 1: Foundation** - 2-3 days
### **Phase 2: Database** - 1-2 days  
### **Phase 3: Google Sheets** - 3-4 days
### **Phase 4: API** - 2-3 days
### **Phase 5: Dashboard** - 2-3 days
### **Phase 6: Testing** - 2-3 days

**Total Estimated Time**: 12-18 days

## 💡 **Implementation Reference**

### **CSV Import Pattern (Based on Existing Code)**
```python
@route("/import-virtual-events", methods=["POST"])
@login_required
def import_virtual_events():
    try:
        sheet_id = os.getenv("VIRTUAL_EVENTS_SHEET_ID")
        if not sheet_id:
            raise ValueError("Virtual Events Sheet ID not configured")

        # Primary URL format
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
        
        try:
            df = pd.read_csv(csv_url)
        except Exception as e:
            # Fallback URL format
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            df = pd.read_csv(csv_url)

        # Process each row and create/update events
        for _, row in df.iterrows():
            # Skip empty rows
            if pd.isna(row["Event Name"]):
                continue
                
            # Create/update virtual event
            event = UpcomingEvent(
                name=row["Event Name"].strip(),
                source="virtual",
                spreadsheet_id=sheet_id,
                # ... map other fields
            )
            db.session.add(event)
            
        db.session.commit()
        return jsonify({"success": True, "imported": len(df)})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400
```

### **Environment Variables Needed**
```bash
VIRTUAL_EVENTS_SHEET_ID=your_google_sheet_id_here
```

### **Spreadsheet Structure Requirements**
- **Column Headers**: Event Name, Date, Time, Available Slots, Event Type, etc.
- **Public Access**: Spreadsheet must be publicly viewable
- **Consistent Format**: Same column structure as Salesforce events where possible

## 🎯 **Next Steps**

1. **Start with Phase 1.1** - Requirements analysis
2. **Set up public Google Spreadsheet for virtual events**
3. **Analyze existing event data structure**
4. **Define virtual event data model**

---

**Note**: This planning document will be archived or deleted upon completion of the feature. Each phase should be completed and tested before moving to the next phase.
