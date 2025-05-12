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
                # Basic validation
                if not all(key in user_data for key in ['username', 'email', 'password_hash']):
                    current_app.logger.warning(f"Skipping user {user_data.get('username', 'unknown')}: Missing required fields")
                    stats['skipped'] += 1
                    continue

                incoming_username = user_data['username']
                incoming_email = user_data['email']

                # Find existing user by email and username
                user_by_email = User.query.filter_by(email=incoming_email).first()
                user_by_username = User.query.filter_by(username=incoming_username).first()

                if user_by_email:
                    # User found by email - primary update target
                    update_username = True
                    if user_by_username and user_by_email.id != user_by_username.id:
                        # Username conflict: incoming username belongs to another user
                        current_app.logger.warning(
                            f"Updating user {user_by_email.username} (ID: {user_by_email.id}, Email: {incoming_email}). "
                            f"Incoming username '{incoming_username}' conflicts with existing user ID {user_by_username.id}. "
                            f"Username will NOT be updated."
                        )
                        update_username = False
                        # Update other fields but skip username

                    # Update existing user found by email
                    if update_username:
                        user_by_email.username = incoming_username
                    # user_by_email.email = incoming_email # Email is the key we found it by, no need to update
                    user_by_email.first_name = user_data.get('first_name')
                    user_by_email.last_name = user_data.get('last_name')
                    user_by_email.security_level = user_data.get('security_level', 0)
                    user_by_email.password_hash = user_data['password_hash']

                    if update_username:
                         stats['updated'] += 1
                         current_app.logger.info(f"Updated user: {user_by_email.username} (found by email: {incoming_email})")
                    else:
                         # Increment skipped or add a dedicated 'conflict' counter if needed
                         stats['skipped'] += 1
                         current_app.logger.info(f"Partially updated user (due to username conflict): {user_by_email.username} (found by email: {incoming_email})")

                elif user_by_username:
                    # User not found by email, but username already exists for a different user
                    current_app.logger.warning(
                        f"Skipping user creation for email {incoming_email}: "
                        f"Username '{incoming_username}' already exists for user ID {user_by_username.id} with email {user_by_username.email}."
                    )
                    stats['skipped'] += 1
                    # Do not proceed with creation

                else:
                    # No existing user found by email or username - safe to create
                    new_user = User(
                        username=incoming_username,
                        email=incoming_email,
                        password_hash=user_data['password_hash'],
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        security_level=user_data.get('security_level', 0)
                    )
                    db.session.add(new_user)
                    stats['created'] += 1
                    current_app.logger.info(f"Created new user: {new_user.username}")

            except Exception as user_error:
                # Rollback changes for this specific user only if absolutely necessary,
                # otherwise let the main rollback handle it.
                # db.session.rollback() # Usually avoid rollback inside the loop unless essential
                current_app.logger.error(f"Error processing user {user_data.get('username', 'unknown')}: {str(user_error)}")
                stats['skipped'] += 1
                continue # Continue to the next user

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