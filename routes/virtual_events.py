"""
Virtual Events Routes

Handles virtual event import from Google Sheets and management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from models import db
from models.upcoming_event import UpcomingEvent
from services.google_sheets_service import GoogleSheetsService
import os
import logging

logger = logging.getLogger(__name__)

virtual_events_bp = Blueprint('virtual_events', __name__)

@virtual_events_bp.route('/api/virtual-events/import', methods=['POST'])
@login_required
def import_virtual_events():
    """
    Import virtual events from Google Sheets.
    
    Expects JSON payload with:
    - sheet_id: Google Sheet ID (optional, will use env var if not provided)
    
    Returns:
        JSON response with import results
    """
    try:
        # Get sheet ID from request or environment
        try:
            data = request.get_json() or {}
        except:
            data = {}
        sheet_id = data.get('sheet_id') or os.getenv('VIRTUAL_EVENTS_SHEET_ID')
        
        if not sheet_id:
            return jsonify({
                'success': False,
                'error': 'Sheet ID not provided and VIRTUAL_EVENTS_SHEET_ID not configured'
            }), 400
        
        logger.info(f"Starting virtual events import from sheet: {sheet_id}")
        
        # Initialize Google Sheets service
        sheets_service = GoogleSheetsService()
        
        # Read data from Google Sheets
        try:
            sheet_data = sheets_service.read_sheet_data(sheet_id)
        except Exception as e:
            logger.error(f"Failed to read sheet data: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to read Google Sheet: {str(e)}'
            }), 400
        
        if not sheet_data:
            return jsonify({
                'success': False,
                'error': 'No data found in Google Sheet'
            }), 400
        
        # Validate sheet structure
        if not sheets_service.validate_sheet_structure(sheet_data):
            return jsonify({
                'success': False,
                'error': 'Google Sheet does not have the expected structure for virtual events'
            }), 400
        
        # Import data using the model method
        try:
            new_count, updated_count, skipped_count = UpcomingEvent.upsert_from_virtual_sheet(
                sheet_data, sheet_id
            )
            
            logger.info(f"Import completed: {new_count} new, {updated_count} updated, {skipped_count} skipped")
            
            return jsonify({
                'success': True,
                'message': 'Virtual events imported successfully',
                'new_count': new_count,
                'updated_count': updated_count,
                'skipped_count': skipped_count,
                'total_processed': len(sheet_data)
            })
            
        except Exception as e:
            logger.error(f"Failed to import virtual events: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Failed to import events: {str(e)}'
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in import_virtual_events: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }), 500

@virtual_events_bp.route('/api/virtual-events', methods=['GET'])
def get_virtual_events():
    """
    Get all virtual events.
    
    Query parameters:
    - status: Filter by status (active, archived)
    - limit: Limit number of results
    
    Returns:
        JSON response with virtual events
    """
    try:
        status = request.args.get('status', 'active')
        limit = request.args.get('limit', type=int)
        
        query = UpcomingEvent.query.filter_by(source='virtual')
        
        if status:
            query = query.filter_by(status=status)
        
        if limit:
            query = query.limit(limit)
        
        events = query.order_by(UpcomingEvent.start_date).all()
        
        return jsonify([event.to_dict() for event in events])
        
    except Exception as e:
        logger.error(f"Error getting virtual events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@virtual_events_bp.route('/api/virtual-events/<int:event_id>', methods=['GET'])
@login_required
def get_virtual_event(event_id):
    """
    Get a specific virtual event by ID.
    
    Args:
        event_id (int): Event ID
        
    Returns:
        JSON response with event data
    """
    try:
        event = UpcomingEvent.query.filter_by(
            id=event_id, 
            source='virtual'
        ).first()
        
        if not event:
            return jsonify({
                'success': False,
                'error': 'Virtual event not found'
            }), 404
        
        return jsonify(event.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting virtual event {event_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@virtual_events_bp.route('/api/virtual-events/sheet-info', methods=['GET'])
@login_required
def get_sheet_info():
    """
    Get information about the configured Google Sheet.
    
    Returns:
        JSON response with sheet information
    """
    try:
        sheet_id = os.getenv('VIRTUAL_EVENTS_SHEET_ID')
        
        if not sheet_id:
            return jsonify({
                'success': False,
                'error': 'VIRTUAL_EVENTS_SHEET_ID not configured'
            }), 400
        
        sheets_service = GoogleSheetsService()
        sheet_info = sheets_service.get_sheet_info(sheet_id)
        
        return jsonify({
            'success': True,
            'sheet_info': sheet_info
        })
        
    except Exception as e:
        logger.error(f"Error getting sheet info: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@virtual_events_bp.route('/api/virtual-events/<int:event_id>/toggle-visibility', methods=['POST'])
@login_required
def toggle_virtual_event_visibility(event_id):
    """
    Toggle visibility of a virtual event.
    
    Args:
        event_id (int): Event ID
        
    Returns:
        JSON response with updated event data
    """
    try:
        event = UpcomingEvent.query.filter_by(
            id=event_id, 
            source='virtual'
        ).first()
        
        if not event:
            return jsonify({
                'success': False,
                'error': 'Virtual event not found'
            }), 404
        
        # Toggle visibility
        event.display_on_website = not event.display_on_website
        db.session.commit()
        
        logger.info(f"Toggled visibility for virtual event {event_id} to {event.display_on_website}")
        
        return jsonify({
            'success': True,
            'message': f'Event visibility {"enabled" if event.display_on_website else "disabled"}',
            'display_on_website': event.display_on_website
        })
        
    except Exception as e:
        logger.error(f"Error toggling virtual event visibility {event_id}: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
