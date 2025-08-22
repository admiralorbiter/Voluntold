# Voluntold: Salesforce Event Management Microservice

A Flask microservice that pipes Salesforce career fair and volunteer event data into various website pages. Staff can manage event visibility, link events to districts, and control what appears on different parts of the website.

## Current Features ✅

### Event Management
- **Salesforce Integration**: Automatic sync with Salesforce `Session__c` objects every 60 minutes
- **Event Visibility Control**: Toggle events on/off for website display
- **Event Notes**: Add/edit notes for volunteers on each event
- **District Linking**: Manually link events to specific school districts
- **Event Status**: Events are automatically archived when full (0 available slots) instead of being deleted

### Archive System (NEW)
- **Smart Event Handling**: Full events are archived instead of deleted, preserving staff configurations
- **Auto-Reactivation**: Archived events automatically become active again if slots become available
- **Archive Dashboard**: View archived events with a toggle button in the admin dashboard
- **Data Preservation**: District links, visibility settings, and notes are maintained when events are archived

### User Interface
- **Admin Dashboard**: Manage all events, visibility, districts, and notes
- **Volunteer Signup Page**: Public-facing page showing available events
- **District-Specific Pages**: Show events linked to specific districts
- **Event-Type Pages**: Filter events by type (Career Jumping, DIA Speaker, etc.)

## Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables** (create `.env` file)
```bash
SF_USERNAME=your_salesforce_username
SF_PASSWORD=your_salesforce_password
SF_SECURITY_TOKEN=your_salesforce_security_token
```

3. **Initialize database**
```bash
python create_admin.py  # Create admin user
python create_jonlane.py  # Create additional user (optional)
```

4. **Run the app**
```bash
python app.py
```

## Testing

### Test Data Creation
```bash
python create_test_data.py  # Populate database with sample events
python test_archive_functionality.py  # Test archive logic
```

### Manual Testing
1. Start the app and go to `/dashboard`
2. Use the "Show Archived" button to toggle between active and archived views
3. Test event visibility toggles
4. Test district linking and note functionality

## Architecture

### Database Models
- **`UpcomingEvent`**: Core event data from Salesforce
- **`SchoolMapping`**: School-to-district mappings
- **`EventDistrictMapping`**: Many-to-many relationship between events and districts
- **`User`**: Admin user authentication

### Key Routes
- **`/dashboard`**: Main admin interface
- **`/events/sync_upcoming_events`**: Salesforce sync endpoint
- **`/volunteer_signup`**: Public volunteer page
- **`/api/events/archive`**: Archived events API

### Sync Process
1. Query Salesforce for future events
2. Archive events with 0 available slots (instead of deleting)
3. Update existing events with new data
4. Add new events to database
5. Delete only past events (start date < yesterday)

## Recent Updates

### Archive Functionality (Latest)
- ✅ Events with 0 available slots are archived instead of deleted
- ✅ Archived events maintain all staff configurations
- ✅ Automatic reactivation when slots become available
- ✅ Archive view in dashboard with toggle button
- ✅ Status badges and visual indicators for archived events

### Previous Improvements
- ✅ Event visibility toggles
- ✅ District linking system
- ✅ Event notes functionality
- ✅ Salesforce sync automation
- ✅ User authentication system

## Next Priorities 🎯

### 1. Automatic District Linking (HIGH PRIORITY)
- **Problem**: Currently requires manual linking of events to districts
- **Goal**: Automatically link events to districts based on school names or other criteria
- **Approach**: Analyze event names/locations and match with district data

### 2. Enhanced Event Filtering
- **Problem**: Limited filtering options for events
- **Goal**: Add search, date range, and type filtering
- **Approach**: Implement client-side filtering and server-side search endpoints

### 3. Virtual Event Support
- **Problem**: No support for virtual/online events
- **Goal**: Handle virtual events with different display logic
- **Approach**: Add virtual event flags and specialized handling

### 4. Event Display Order Control
- **Problem**: Events display in chronological order only
- **Goal**: Allow staff to control event display order
- **Approach**: Add priority/order fields and sorting options

## Technical Debt & Improvements

### Code Quality
- Add comprehensive test coverage
- Implement proper error handling and logging
- Add input validation and sanitization
- Improve code documentation

### Performance
- Add database indexing for common queries
- Implement caching for district data
- Optimize Salesforce sync process
- Add pagination for large event lists

### Security
- Implement rate limiting
- Add CSRF protection
- Validate Salesforce data integrity
- Secure admin endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions:
1. Check the console logs for JavaScript errors
2. Verify Salesforce credentials and permissions
3. Check database connectivity
4. Review the sync logs in the terminal

---

**Current Status**: ✅ Archive system implemented and working
**Next Focus**: 🔄 Automatic district linking system
**Production Ready**: ✅ Yes, with manual district management
