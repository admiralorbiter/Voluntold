import pytest
import json
from datetime import datetime, timezone
from models.upcoming_event import UpcomingEvent
from models import db

def create_mock_event(
    event_id='SF_TEST_120',
    name='Test Public Event',
    available_slots=15,
    filled_jobs=5,
    date_and_time='02/10/2026 10:00 AM to 11:00 AM',
    event_type='In-Person',
    registration_link='https://example.com/mock-register',
    display_on_website=True,
    start_date=datetime(2026, 2, 10, tzinfo=timezone.utc),
    note='This is a test description for TC-120.'
):
    """Helper to create a database event"""
    event = UpcomingEvent(
        salesforce_id=event_id,
        name=name,
        available_slots=available_slots,
        filled_volunteer_jobs=filled_jobs,
        date_and_time=date_and_time,
        event_type=event_type,
        registration_link=registration_link,
        display_on_website=display_on_website,
        start_date=start_date,
        note=note,
        source='salesforce',
        status='active'
    )
    return event

class TestPublicPageDisplayAPI:
    """Test suite for TC-120 and TC-121"""

    def test_public_page_event_fields_tc_120(self, client, app):
        """
        TC-120: Event display fields
        Verify public API shows slots, filled, date, description (note).
        """
        with app.app_context():
            # Setup: Clear existing and add a specific test event
            UpcomingEvent.query.delete()
            mock_event = create_mock_event()
            db.session.add(mock_event)
            db.session.commit()

            # Action: Call the API used by the signup page
            response = client.get('/events/volunteer_signup_api')
            assert response.status_code == 200
            
            data = response.get_json()
            assert len(data) > 0
            
            # Find our specific event in the response
            event_data = next((e for e in data if e['Id'] == 'SF_TEST_120'), None)
            assert event_data is not None, "Test event should be in API response"

            # Assertions for TC-120: Verify fields are present
            # Note: The API returns both camelCase (Salesforce style) and snake_case versions
            assert 'available_slots' in event_data or 'Available_Slots__c' in event_data
            assert 'filled_volunteer_jobs' in event_data or 'Filled_Volunteer_Jobs__c' in event_data
            assert 'date_and_time' in event_data or 'Date_and_Time_for_Cal__c' in event_data
            assert 'note' in event_data

    def test_field_accuracy_tc_121(self, client, app):
        """
        TC-121: Field accuracy
        Verify displayed values match Salesforce source (the database record).
        """
        expected_slots = 25
        expected_filled = 10
        expected_date = '03/15/2026 1:00 PM to 2:00 PM'
        expected_note = 'Accuracy test description.'
        expected_name = 'Accuracy Test Event'

        with app.app_context():
            # Setup
            UpcomingEvent.query.delete()
            mock_event = create_mock_event(
                event_id='SF_ACCURACY_121',
                name=expected_name,
                available_slots=expected_slots,
                filled_jobs=expected_filled,
                date_and_time=expected_date,
                note=expected_note,
                start_date=datetime(2026, 3, 15, tzinfo=timezone.utc)
            )
            db.session.add(mock_event)
            db.session.commit()

            # Action
            response = client.get('/events/volunteer_signup_api')
            data = response.get_json()
            event_data = next((e for e in data if e['Id'] == 'SF_ACCURACY_121'), None)
            
            # Assertions for TC-121: Verify values match exactly
            assert event_data['Name'] == expected_name
            assert event_data['available_slots'] == expected_slots
            assert event_data['filled_volunteer_jobs'] == expected_filled
            assert event_data['date_and_time'] == expected_date
            assert event_data['note'] == expected_note
