# Archive System: How It Works

## 🎯 **Overview**

The archive system prevents the loss of staff-configured event settings when events fill up. Instead of deleting full events, they are archived and can be reactivated when slots become available again.

## 🔄 **How Archive Reactivation Works**

### **1. Event Becomes Full (0 Available Slots)**
```
Salesforce Event: "Allen Village Career Fair" - 0 available slots
↓
System Action: Status changed from 'active' → 'archived'
↓
Result: Event disappears from volunteer signup page but retains all settings
```

### **2. People Drop Out - Slots Become Available**
```
Salesforce Event: "Allen Village Career Fair" - 3 available slots (people dropped out)
↓
System Action: During next sync, status automatically changes from 'archived' → 'active'
↓
Result: Event reappears on volunteer signup page with all previous settings intact
```

## 📋 **What Gets Preserved When Events Are Archived**

### ✅ **Preserved Settings**
- **District Links**: All linked districts remain connected
- **Visibility Toggle**: Website display setting is maintained
- **Event Notes**: Staff notes for volunteers are preserved
- **Custom Configurations**: Any other staff settings remain intact

### 🔄 **What Changes**
- **Status Field**: Only the `status` field changes from 'active' to 'archived'
- **Display Logic**: Event no longer shows on public volunteer page
- **Dashboard View**: Event appears in "Archived Events" view

## 🧠 **Technical Implementation**

### **Archive Logic (in `routes/upcoming_events.py`)**
```python
# Archive full events instead of deleting them
archived_count = UpcomingEvent.query.filter(
    UpcomingEvent.available_slots <= 0
).update({'status': 'archived'})
```

### **Reactivation Logic (in `models/upcoming_event.py`)**
```python
# If event becomes available again, reactivate it
if existing.status == 'archived' and event_data['available_slots'] > 0:
    existing.status = 'active'
    print(f"Reactivating archived event: {existing.name}")
```

## 📊 **Sync Process Flow**

```
1. Salesforce API Query
   ↓
2. Check Each Event
   ↓
3. If Event Exists in Database:
   ├── Update event data
   ├── Check if archived event has slots > 0
   │   ├── YES → Reactivate (status: 'archived' → 'active')
   │   └── NO → Keep archived
   └── Preserve all staff settings
   ↓
4. If New Event:
   ├── Add to database
   └── Set status: 'active'
   ↓
5. Archive Full Events:
   ├── Find events with 0 available slots
   └── Change status to 'archived'
```

## 🎭 **User Experience**

### **For Staff (Dashboard)**
1. **Event Fills Up**: Event automatically moves to "Archived Events" view
2. **People Drop Out**: Event automatically moves back to "Active Events" view
3. **All Settings Preserved**: No need to reconfigure district links, notes, or visibility

### **For Volunteers (Public Page)**
1. **Event Fills Up**: Event disappears from volunteer signup page
2. **People Drop Out**: Event reappears on volunteer signup page
3. **Seamless Experience**: No interruption to volunteer workflow

## 🔍 **Monitoring & Debugging**

### **Console Logs**
When events are reactivated, you'll see:
```
Reactivating archived event: Allen Village Career Fair
```

### **Dashboard Status**
- **Active Events**: Shows current available events
- **Archived Events**: Shows full events that are no longer accepting volunteers
- **Toggle Button**: Switch between views to monitor both sets

### **Sync Results**
The sync process reports:
```
Archived: 5 full events
Deleted: 2 past events
Updated: 15 existing events
New: 3 new events
```

## ⚠️ **Edge Cases & Considerations**

### **Multiple Status Changes**
- An event can be archived and reactivated multiple times
- Each cycle preserves all settings
- No data loss occurs during status transitions

### **Sync Timing**
- Reactivation happens during the next scheduled sync (every 60 minutes)
- Manual sync can trigger immediate reactivation
- No real-time status updates (batch processing)

### **Data Integrity**
- All database relationships are maintained
- No orphaned district links or notes
- Event history is preserved

## 🧪 **Testing the System**

### **Test Scripts**
```bash
# Create test events with 0 slots
python scripts/create_test_data.py

# Test archive functionality
python scripts/test_archive_functionality.py
```

### **Manual Testing**
1. Create an event with 0 available slots
2. Verify it appears in "Archived Events" view
3. Manually change available slots to > 0
4. Run sync to see reactivation
5. Verify event returns to "Active Events" view

## 🎯 **Benefits of This Approach**

### **Before (Deletion System)**
- ❌ Lost district links when events filled up
- ❌ Lost staff notes and configurations
- ❌ Required manual reconfiguration when slots became available
- ❌ Poor user experience for staff

### **After (Archive System)**
- ✅ All settings preserved when events fill up
- ✅ Automatic reactivation when slots become available
- ✅ No manual reconfiguration needed
- ✅ Seamless staff experience
- ✅ Better data integrity

## 🚀 **Future Enhancements**

### **Potential Improvements**
- **Real-time Updates**: WebSocket notifications for status changes
- **Audit Trail**: Track all archive/reactivation events
- **Manual Override**: Allow staff to force archive/reactivation
- **Bulk Operations**: Archive/reactivate multiple events at once

---

**Key Takeaway**: The archive system ensures that staff never lose their work configuring events, while providing a seamless experience for both staff and volunteers.
