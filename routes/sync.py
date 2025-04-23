from flask import Blueprint, jsonify, current_app
from flask_login import login_required
from models import db
from models.user import User
import requests
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sync_bp = Blueprint('sync', __name__)

@sync_bp.route('/sync_users', methods=['POST'])
@login_required
def sync_users():
    """
    Sync users from the external source to the local database.
    """
    try:
        # Get credentials from environment variables
        sync_username = os.getenv('SYNC_USERNAME')
        sync_password = os.getenv('SYNC_PASSWORD')

        if not sync_username or not sync_password:
            error_message = "Sync credentials not found in environment variables"
            current_app.logger.error(error_message)
            return jsonify({'success': False, 'error': error_message}), 500

        # Step 1: Generate the API token
        token_response = requests.post(
            'https://polaris-prepkc.pythonanywhere.com/api/v1/token',
            headers={'Content-Type': 'application/json'},
            json={
                'username': sync_username,
                'password': sync_password
            }
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        api_token = token_data.get('token')

        if not api_token:
            return jsonify({'success': False, 'error': 'Failed to obtain API token'}), 401

        # Step 2: Fetch users from the external API with the token
        headers = {
            'Content-Type': 'application/json',
            'X-API-Token': api_token
        }
        response = requests.get('https://polaris-prepkc.pythonanywhere.com/api/v1/users/sync', headers=headers)
        response.raise_for_status()
        external_users = response.json().get('users', [])

        # Track statistics
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0
        }

        # Process each user
        for user_data in external_users:
            try:
                if not all(key in user_data for key in ['username', 'email', 'password_hash']):
                    current_app.logger.warning(f"Skipping user {user_data.get('username', 'unknown')}: Missing required fields")
                    stats['skipped'] += 1
                    continue

                # Find existing user or create a new one
                user = User.query.filter_by(email=user_data['email']).first()
                
                if user:
                    # Update existing user
                    user.username = user_data['username']
                    user.email = user_data['email']
                    user.first_name = user_data.get('first_name')
                    user.last_name = user_data.get('last_name')
                    user.security_level = user_data.get('security_level', 0)
                    user.password_hash = user_data['password_hash']
                    stats['updated'] += 1
                    current_app.logger.info(f"Updated user: {user.username}")
                else:
                    # Create new user with the provided password hash
                    new_user = User(
                        username=user_data['username'],
                        email=user_data['email'],
                        password_hash=user_data['password_hash'],
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        security_level=user_data.get('security_level', 0)
                    )
                    db.session.add(new_user)
                    stats['created'] += 1
                    current_app.logger.info(f"Created new user: {new_user.username}")

            except Exception as user_error:
                current_app.logger.error(f"Error processing user {user_data.get('username', 'unknown')}: {str(user_error)}")
                stats['skipped'] += 1
                continue

        # Commit changes to the database
        db.session.commit()

        success_message = (
            f"Sync completed successfully. "
            f"Created: {stats['created']}, "
            f"Updated: {stats['updated']}, "
            f"Skipped: {stats['skipped']} users"
        )
        current_app.logger.info(success_message)

        return jsonify({
            'success': True,
            'message': success_message,
            'stats': stats
        }), 200

    except Exception as e:
        db.session.rollback()
        error_message = f"Error syncing users: {str(e)}"
        current_app.logger.error(error_message)
        return jsonify({'success': False, 'error': error_message}), 500