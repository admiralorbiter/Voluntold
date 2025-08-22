#!/usr/bin/env python3
"""
Test Data Creation Script for Voluntold
Creates sample events with different statuses for testing archive functionality
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
from models.event_district_mapping import EventDistrictMapping

def create_test_events():
    """Create test events with various statuses"""
    
    # Clear existing test data (optional - comment out if you want to keep existing)
    print("Clearing existing test events...")
    UpcomingEvent.query.filter(UpcomingEvent.name.like('TEST_%')).delete()
    db.session.commit()
    
    # Create test events
    test_events = [
        {
            'name': 'TEST_Active Event - Career Jumping',
            'salesforce_id': 'TEST_001',
            'available_slots': 5,
            'filled_volunteer_jobs': 3,
            'date_and_time': '12/15/2025 9:00 AM to 11:00 AM',
            'event_type': 'Career Jumping',
            'registration_link': 'https://example.com/register1',
            'display_on_website': True,
            'start_date': datetime.now(timezone.utc) + timedelta(days=30),
            'status': 'active'
        },
        {
            'name': 'TEST_Active Event - DIA Speaker',
            'salesforce_id': 'TEST_002',
            'available_slots': 2,
            'filled_volunteer_jobs': 0,
            'date_and_time': '12/20/2025 10:00 AM to 11:00 AM',
            'event_type': 'DIA - Classroom Speaker',
            'registration_link': 'https://example.com/register2',
            'display_on_website': False,
            'start_date': datetime.now(timezone.utc) + timedelta(days=35),
            'status': 'active'
        },
        {
            'name': 'TEST_Archived Event - Full Career Fair',
            'salesforce_id': 'TEST_003',
            'available_slots': 0,
            'filled_volunteer_jobs': 25,
            'date_and_time': '12/10/2025 8:00 AM to 12:00 PM',
            'event_type': 'Career Fair',
            'registration_link': 'https://example.com/register3',
            'display_on_website': True,
            'start_date': datetime.now(timezone.utc) + timedelta(days=25),
            'status': 'archived'
        },
        {
            'name': 'TEST_Archived Event - Full Orientation',
            'salesforce_id': 'TEST_004',
            'available_slots': 0,
            'filled_volunteer_jobs': 20,
            'date_and_time': '12/05/2025 1:00 PM to 2:00 PM',
            'event_type': 'Volunteer Orientation',
            'registration_link': 'https://example.com/register4',
            'display_on_website': False,
            'start_date': datetime.now(timezone.utc) + timedelta(days=20),
            'status': 'archived'
        },
        {
            'name': 'TEST_Past Event - Should be Deleted',
            'salesforce_id': 'TEST_005',
            'available_slots': 10,
            'filled_volunteer_jobs': 5,
            'date_and_time': '11/01/2025 9:00 AM to 11:00 AM',
            'event_type': 'Career Speaker',
            'registration_link': 'https://example.com/register5',
            'display_on_website': True,
            'start_date': datetime.now(timezone.utc) - timedelta(days=5),
            'status': 'active'
        }
    ]
    
    print("Creating test events...")
    created_events = []
    
    for event_data in test_events:
        event = UpcomingEvent(**event_data)
        db.session.add(event)
        created_events.append(event)
    
    db.session.commit()
    print(f"Created {len(created_events)} test events")
    
    # Add some district mappings to test events
    print("Adding district mappings...")
    districts = ['Grandview School District', 'Independence School District', 'Kansas City Kansas Public Schools']
    
    for i, event in enumerate(created_events):
        # Add 1-2 districts to each event
        event_districts = districts[i % len(districts):(i % len(districts)) + 1]
        for district in event_districts:
            mapping = EventDistrictMapping(event_id=event.id, district=district)
            db.session.add(mapping)
    
    db.session.commit()
    print("Added district mappings")
    
    # Display summary
    print("\n" + "="*50)
    print("TEST DATA SUMMARY")
    print("="*50)
    
    active_events = UpcomingEvent.query.filter_by(status='active').all()
    archived_events = UpcomingEvent.query.filter_by(status='archived').all()
    
    print(f"Active Events: {len(active_events)}")
    for event in active_events:
        print(f"  - {event.name} (Slots: {event.available_slots}, Display: {event.display_on_website})")
    
    print(f"\nArchived Events: {len(archived_events)}")
    for event in archived_events:
        print(f"  - {event.name} (Slots: {event.available_slots}, Display: {event.display_on_website})")
    
    print("\n" + "="*50)
    print("Next steps:")
    print("1. Run: python sync_script.py")
    print("2. Check: /dashboard (should only show active events)")
    print("3. Check: /dashboard/archive (should show archived events)")
    print("4. Check: /volunteer_signup (should only show active + visible events)")
    print("="*50)

def clear_test_data():
    """Clear all test data"""
    print("Clearing all test data...")
    UpcomingEvent.query.filter(UpcomingEvent.name.like('TEST_%')).delete()
    db.session.commit()
    print("Test data cleared!")

if __name__ == '__main__':
    with app.app_context():
        if len(sys.argv) > 1 and sys.argv[1] == '--clear':
            clear_test_data()
        else:
            create_test_events()
