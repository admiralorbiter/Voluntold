"""
Test cases for Salesforce sync functionality on UpcomingEvent model.

TC-102: Idempotency - No duplicates on double sync
TC-103: Update propagates - Changed slots reflected in VT
"""
import pytest
from datetime import datetime, timezone
from models import db
from models.upcoming_event import UpcomingEvent


def create_mock_salesforce_event(
    event_id='SF001',
    name='Test Event',
    available_slots=10,
    filled_jobs=2,
    date_and_time='01/25/2026 9:00 AM to 10:00 AM',
    event_type='In-Person',
    registration_link='https://example.com/register',
    display_on_website='Yes',
    start_date='2026-01-25'
):
    """Helper to create mock Salesforce event data"""
    return {
        'Id': event_id,
        'Name': name,
        'Available_Slots__c': available_slots,
        'Filled_Volunteer_Jobs__c': filled_jobs,
        'Date_and_Time_for_Cal__c': date_and_time,
        'Session_Type__c': event_type,
        'Registration_Link__c': registration_link,
        'Display_on_Website__c': display_on_website,
        'Start_Date__c': start_date
    }


class TestSalesforceSync:
    """Test suite for Salesforce sync functionality"""

    def test_idempotency_no_duplicates_on_double_sync(self, app):
        """
        TC-102: Idempotency - No duplicates on double sync
        
        Syncing the same Salesforce event twice should:
        1. Create exactly 1 record in the database (not 2)
        2. First sync returns new_count=1, updated_count=0
        3. Second sync returns new_count=0, updated_count=1
        """
        with app.app_context():
            # Arrange: Create mock Salesforce data
            sf_event = create_mock_salesforce_event(
                event_id='SF_IDEM_001',
                name='Idempotency Test Event',
                available_slots=5
            )
            sf_data = [sf_event]
            
            # Act: First sync
            new_count_1, updated_count_1 = UpcomingEvent.upsert_from_salesforce(sf_data)
            
            # Assert: First sync creates new record
            assert new_count_1 == 1, "First sync should create 1 new record"
            assert updated_count_1 == 0, "First sync should not update any records"
            
            # Count records after first sync
            count_after_first = UpcomingEvent.query.filter_by(
                salesforce_id='SF_IDEM_001'
            ).count()
            assert count_after_first == 1, "Should have exactly 1 record after first sync"
            
            # Act: Second sync with identical data
            new_count_2, updated_count_2 = UpcomingEvent.upsert_from_salesforce(sf_data)
            
            # Assert: Second sync updates existing record (no new record created)
            assert new_count_2 == 0, "Second sync should not create new records"
            assert updated_count_2 == 1, "Second sync should update 1 existing record"
            
            # Count records after second sync - should still be 1
            count_after_second = UpcomingEvent.query.filter_by(
                salesforce_id='SF_IDEM_001'
            ).count()
            assert count_after_second == 1, "Should still have exactly 1 record after double sync (no duplicates)"

    def test_update_propagates_changed_slots_reflected(self, app):
        """
        TC-103: Update propagates - Changed slots reflected in VT
        
        When Salesforce data changes (e.g., slots are updated),
        running sync again should update the local database with new values.
        """
        with app.app_context():
            # Arrange: Create initial mock Salesforce data
            initial_available_slots = 10
            initial_filled_jobs = 2
            
            sf_event = create_mock_salesforce_event(
                event_id='SF_UPDATE_001',
                name='Update Propagation Test Event',
                available_slots=initial_available_slots,
                filled_jobs=initial_filled_jobs
            )
            sf_data = [sf_event]
            
            # Act: First sync to insert the event
            UpcomingEvent.upsert_from_salesforce(sf_data)
            
            # Verify initial values
            event = UpcomingEvent.query.filter_by(salesforce_id='SF_UPDATE_001').first()
            assert event is not None, "Event should exist after first sync"
            assert event.available_slots == initial_available_slots, "Initial available_slots should match"
            assert event.filled_volunteer_jobs == initial_filled_jobs, "Initial filled_jobs should match"
            
            # Arrange: Update the Salesforce data with new slot values
            updated_available_slots = 3
            updated_filled_jobs = 9
            
            sf_event_updated = create_mock_salesforce_event(
                event_id='SF_UPDATE_001',  # Same ID
                name='Update Propagation Test Event',
                available_slots=updated_available_slots,
                filled_jobs=updated_filled_jobs
            )
            sf_data_updated = [sf_event_updated]
            
            # Act: Second sync with updated data
            new_count, updated_count = UpcomingEvent.upsert_from_salesforce(sf_data_updated)
            
            # Assert: Sync reports an update
            assert new_count == 0, "Should not create new record for existing event"
            assert updated_count == 1, "Should update existing record"
            
            # Re-query the event to get fresh data
            event_refreshed = UpcomingEvent.query.filter_by(salesforce_id='SF_UPDATE_001').first()
            
            # Assert: Values are updated
            assert event_refreshed.available_slots == updated_available_slots, \
                f"available_slots should be updated to {updated_available_slots}, got {event_refreshed.available_slots}"
            assert event_refreshed.filled_volunteer_jobs == updated_filled_jobs, \
                f"filled_volunteer_jobs should be updated to {updated_filled_jobs}, got {event_refreshed.filled_volunteer_jobs}"

    def test_update_propagates_other_fields(self, app):
        """
        TC-103 Extended: Verify other fields also update correctly
        """
        with app.app_context():
            # Initial event
            sf_event = create_mock_salesforce_event(
                event_id='SF_UPDATE_002',
                name='Original Name',
                event_type='In-Person',
                date_and_time='01/25/2026 9:00 AM'
            )
            UpcomingEvent.upsert_from_salesforce([sf_event])
            
            # Update multiple fields
            sf_event_updated = create_mock_salesforce_event(
                event_id='SF_UPDATE_002',
                name='Updated Name',
                event_type='Virtual',
                date_and_time='01/26/2026 2:00 PM'
            )
            UpcomingEvent.upsert_from_salesforce([sf_event_updated])
            
            # Verify updates
            event = UpcomingEvent.query.filter_by(salesforce_id='SF_UPDATE_002').first()
            assert event.name == 'Updated Name', "Name should be updated"
            assert event.event_type == 'Virtual', "Event type should be updated"
            assert event.date_and_time == '01/26/2026 2:00 PM', "Date/time should be updated"
