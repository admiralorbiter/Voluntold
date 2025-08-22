#!/usr/bin/env python3
"""
Quick test script to verify archive functionality
"""

import os
import sys
from datetime import datetime, timedelta, timezone

# Add the project root to the path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import app
from models import db
from models.upcoming_event import UpcomingEvent

def test_archive_functionality():
    """Test the archive functionality"""
    
    with app.app_context():
        print("Testing Archive Functionality")
        print("=" * 40)
        
        # Check current events
        active_events = UpcomingEvent.query.filter_by(status='active').all()
        archived_events = UpcomingEvent.query.filter_by(status='archived').all()
        
        print(f"Active Events: {len(active_events)}")
        for event in active_events:
            print(f"  - {event.name} (Slots: {event.available_slots}, Display: {event.display_on_website})")
        
        print(f"\nArchived Events: {len(archived_events)}")
        for event in archived_events:
            print(f"  - {event.name} (Slots: {event.available_slots}, Display: {event.display_on_website})")
        
        # Test the sync logic manually
        print("\n" + "=" * 40)
        print("Testing Manual Archive Logic")
        print("=" * 40)
        
        # Find events that should be archived (0 available slots)
        events_to_archive = UpcomingEvent.query.filter(
            UpcomingEvent.available_slots <= 0,
            UpcomingEvent.status == 'active'
        ).all()
        
        if events_to_archive:
            print(f"Events that should be archived: {len(events_to_archive)}")
            for event in events_to_archive:
                print(f"  - {event.name} (Slots: {event.available_slots})")
                # Manually archive them for testing
                event.status = 'archived'
            
            db.session.commit()
            print("Events archived successfully!")
        else:
            print("No events need archiving")
        
        # Check final state
        active_events = UpcomingEvent.query.filter_by(status='active').all()
        archived_events = UpcomingEvent.query.filter_by(status='archived').all()
        
        print(f"\nFinal State:")
        print(f"Active Events: {len(active_events)}")
        print(f"Archived Events: {len(archived_events)}")
        
        print("\n" + "=" * 40)
        print("Test Complete!")
        print("=" * 40)
        print("Next steps:")
        print("1. Start your app: python app.py")
        print("2. Go to /dashboard")
        print("3. Click 'Show Archived' button")
        print("4. Verify archived events appear with 'Archived' badge")

if __name__ == '__main__':
    test_archive_functionality()
