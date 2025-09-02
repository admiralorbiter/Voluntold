# User Workflow: PREP-KC Staff Event Management

## 👥 **Who Uses This System**

### **Primary Users**
- **PREP-KC Staff**: Event coordinators and volunteer managers
- **Admin Users**: System administrators with full access
- **Volunteers**: End users who sign up for events (via website)

## 🔄 **Current Staff Workflow**

### **Step 1: Event Creation in Salesforce**
```
Staff creates new event in Salesforce
├── Event Name: "Grandview High School Career Fair"
├── Date & Time: "03/15/2024 9:00 AM to 2:00 PM"
├── Available Slots: 25
├── Event Type: "Career Fair"
├── Registration Link: [URL]
└── Display on Website: Yes/No
```

### **Step 2: Wait for Sync (or Manual Sync)**
```
System automatically syncs every 60 minutes
OR
Staff clicks "Sync Events" button in dashboard
↓
Event appears in admin dashboard
```

### **Step 3: Manual District Linking (Current Pain Point)**
```
Staff must manually link event to districts:
├── Click "Add District" button
├── Search for district name
├── Select appropriate district(s)
└── Repeat for each district the event serves
```

### **Step 4: Configure Event Display**
```
Staff sets event visibility:
├── Toggle "Display on Website" ON/OFF
├── Add notes for volunteers (optional)
└── Verify event appears on correct pages
```

### **Step 5: Monitor Event Status**
```
Staff monitors event throughout its lifecycle:
├── Check available slots
├── Update notes as needed
├── Handle district changes
└── Manage event visibility
```

## 📱 **Dashboard Interface**

### **Main Dashboard View**
```
┌─────────────────────────────────────────────────────────┐
│ Dashboard                                    [Sync] [Archive] │
├─────────────────────────────────────────────────────────┤
│ Events are synced every 60 minutes                      │
│ Use toggle to show/hide events on website               │
│ Use "Show Archived" to view full events                 │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Event: Grandview High School Career Fair                │
│ Date: 03/15/2024 9:00 AM - 2:00 PM                     │
│ Slots: 15/25 available                                  │
│ Status: [Active] [Toggle ON] [Add District] [Notes]    │
│ Districts: Grandview School District                    │
└─────────────────────────────────────────────────────────┘
```

### **Archive View**
```
┌─────────────────────────────────────────────────────────┐
│ Archived Events (Full - No Available Slots)            │
├─────────────────────────────────────────────────────────┤
│ Event: Independence High Career Fair                    │
│ Date: 03/10/2024 9:00 AM - 2:00 PM                     │
│ Slots: 0/20 available (FULL)                           │
│ Status: [Archived] [Toggle OFF] [View Districts]       │
│ Districts: Independence School District                 │
└─────────────────────────────────────────────────────────┘
```

## 🎯 **Current Pain Points & Solutions**

### **Pain Point 1: Manual District Linking**
**Current Process:**
```
For each event:
1. Click "Add District" button
2. Type district name in search box
3. Select from dropdown
4. Repeat for multiple districts
5. Verify correct districts are linked
```

**Time Impact:**
- 2-3 minutes per event
- 20-30 events per month
- 40-90 minutes of manual work monthly

**Proposed Solution:**
- Automatic district detection from event names
- Confidence scoring for automatic assignments
- Manual override for edge cases
- Reduce manual work by 80%

### **Pain Point 2: Event Visibility Management**
**Current Process:**
```
Staff must remember to:
1. Toggle events ON for volunteer signup page
2. Link to correct districts for district pages
3. Verify DIA events appear on DIA page
4. Monitor event status changes
```

**Proposed Solution:**
- Smart defaults based on event type
- Bulk operations for multiple events
- Visual indicators for event status
- Automated notifications for status changes

### **Pain Point 3: Event Status Monitoring**
**Current Process:**
```
Staff must manually:
1. Check dashboard regularly
2. Monitor available slots
3. Update notes as needed
4. Handle district changes
```

**Proposed Solution:**
- Real-time status updates
- Automated notifications
- Bulk update capabilities
- Event history tracking

## 📊 **Event Display Logic**

### **Volunteer Signup Page**
**Shows events where:**
- `display_on_website = true`
- `status = 'active'`
- `available_slots > 0`

### **District Pages**
**Shows events where:**
- Event is linked to that specific district
- `display_on_website = true`
- `status = 'active'`

### **DIA Events Page**
**Shows events where:**
- `event_type = 'DIA'`
- `status = 'active'`
- (Automatic - no manual configuration needed)

### **Archived Events**
**Shows events where:**
- `status = 'archived'`
- `available_slots = 0`
- (Full events that are no longer accepting volunteers)

## 🔧 **Common Tasks**

### **Adding a New Event**
1. Create event in Salesforce
2. Wait for sync or manually sync
3. Link to appropriate districts
4. Toggle visibility ON
5. Add notes for volunteers
6. Verify event appears on correct pages

### **Managing a Full Event**
1. Event automatically archives when slots = 0
2. Event disappears from volunteer signup page
3. All settings are preserved
4. Event can be reactivated if slots become available

### **Updating Event Information**
1. Update in Salesforce
2. Sync changes
3. Verify district links are still correct
4. Update notes if needed
5. Check visibility settings

### **Handling District Changes**
1. Remove old district links
2. Add new district links
3. Verify event appears on correct pages
4. Update notes if needed

## 🎯 **Success Metrics**

### **Current Performance**
- **Sync Time**: ~30 seconds for 50 events
- **Manual Linking**: 2-3 minutes per event
- **Error Rate**: ~5% manual linking errors
- **Staff Satisfaction**: Moderate (due to manual work)

### **Target Performance**
- **Sync Time**: <30 seconds for 100+ events
- **Automatic Linking**: 90%+ accuracy
- **Manual Override**: <10% of events need manual adjustment
- **Staff Satisfaction**: High (automated workflow)

## 🚀 **Future Workflow (With Automatic District Linking)**

### **Streamlined Process**
```
1. Create event in Salesforce
2. Wait for sync
3. Review automatic district assignments
4. Override if needed (10% of cases)
5. Toggle visibility
6. Add notes
7. Done!
```

### **Time Savings**
- **Before**: 3-4 minutes per event
- **After**: 1-2 minutes per event
- **Monthly Savings**: 20-40 minutes
- **Annual Savings**: 4-8 hours

---

**Key Takeaway**: The current workflow works but requires significant manual effort. Automatic district linking will reduce staff workload while maintaining accuracy and control.
