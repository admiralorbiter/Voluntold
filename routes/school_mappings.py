from flask import Blueprint, jsonify, request
from pathlib import Path
from models import db
from models.school_mapping import SchoolMapping
from flask_login import login_required
import os

bp = Blueprint('school_mappings', __name__)

# Get the absolute path to the directory containing your application
BASE_DIR = Path(__file__).resolve().parent.parent

# Configure the path to your CSV file
MAPPINGS_FILE = Path(os.getenv('SCHOOL_MAPPINGS_PATH', BASE_DIR / 'data' / 'school-mappings.csv'))

@bp.route('/api/school-mappings', methods=['GET'])
def get_mappings():
    """Get all school mappings from database"""
    try:
        mappings = SchoolMapping.query.all()
        return jsonify([mapping.to_dict() for mapping in mappings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/school-mappings/sync', methods=['POST'])
def sync_mappings():
    """Sync mappings from CSV to database"""
    try:
        # Load mappings from CSV
        csv_mappings = SchoolMapping.load_from_csv(MAPPINGS_FILE)
        
        # Clear existing mappings
        SchoolMapping.query.delete()
        
        # Add new mappings to database
        for mapping in csv_mappings:
            db.session.add(mapping)
        
        # Commit changes
        db.session.commit()
        
        # Return the loaded mappings
        return jsonify({
            'message': f'Successfully synced {len(csv_mappings)} school mappings to database',
            'data': [mapping.to_dict() for mapping in csv_mappings]
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/api/school-mappings/district/<district>', methods=['GET'])
def get_schools_by_district(district):
    """Get all schools for a specific district from database"""
    try:
        mappings = SchoolMapping.query.filter_by(district=district).all()
        return jsonify([mapping.to_dict() for mapping in mappings])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/schools/search')
@login_required
def search_schools():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    schools = SchoolMapping.query.filter(
        db.or_(
            SchoolMapping.name.ilike(f'%{query}%'),
            SchoolMapping.district.ilike(f'%{query}%')
        )
    ).limit(10).all()
    
    return jsonify([school.to_dict() for school in schools]) 