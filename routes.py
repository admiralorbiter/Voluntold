from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
import requests
from forms import LoginForm
from models import User, db, Session
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from simple_salesforce import Salesforce, SalesforceAuthenticationFailed

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid username or password.', 'danger')
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index')) 
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get initial events from database and convert to dict
        events = [event.to_dict() for event in Session.query.all()]
        return render_template('dashboard.html', initial_events=events)
    
    @app.route('/events')
    @login_required
    def get_events():
        try:
            print(f"Attempting to connect with: {Config.SF_USERNAME}")
            
            sf = Salesforce(
                username=Config.SF_USERNAME,
                password=Config.SF_PASSWORD,
                security_token=Config.SF_SECURITY_TOKEN,
                domain='login'
            )

            query = """
                SELECT Id, Name, Available_slots__c, Filled_Volunteer_Jobs__c, 
                Date_and_Time_for_Cal__c, Session_Type__c, Registration_Link__c, 
                Display_on_Website__c, Start_Date__c 
                FROM Session__c 
                WHERE Start_Date__c > TODAY and Available_Slots__c>0 
                ORDER BY Start_Date__c ASC
            """
            result = sf.query(query)
            events = result.get('records', [])

            # Store the data
            new_count, updated_count = Session.upsert_from_salesforce(events)
            
            # Get updated events from database where display_on_website is True
            updated_events = Session.query.filter_by(display_on_website=True).all()
            
            return jsonify({
                'success': True,
                'message': f'Successfully synced: {new_count} new, {updated_count} updated',
                'events': [event.to_dict() for event in updated_events]
            })

        except SalesforceAuthenticationFailed as e:
            return jsonify({
                'success': False,
                'message': 'Failed to authenticate with Salesforce'
            }), 401

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'An unexpected error occurred: {str(e)}'
            }), 500
    
    @app.route('/signup')
    def signup():
        # Get initial events from database where display_on_website is True, ordered by date
        events = [event.to_dict() for event in Session.query.filter_by(display_on_website=True).order_by(Session.start_date).all()]
        return render_template('signup.html', initial_events=events)
    
    @app.route('/toggle-event-visibility', methods=['POST'])
    @login_required
    def toggle_event_visibility():
        try:
            data = request.get_json()
            event_id = data.get('event_id')
            visible = data.get('visible')
            
            print(f"Toggling event {event_id} to visibility: {visible}")  # Debug log
            
            event = Session.query.filter_by(salesforce_id=event_id).first()
            if not event:
                print(f"Event not found with ID: {event_id}")  # Debug log
                return jsonify({
                    'success': False,
                    'message': 'Event not found'
                }), 404
            
            # Print before state
            print(f"Before update - Event {event_id} visibility: {event.display_on_website}")
            
            event.display_on_website = visible
            db.session.commit()
            
            # Verify the update
            db.session.refresh(event)
            print(f"After update - Event {event_id} visibility: {event.display_on_website}")
            
            return jsonify({
                'success': True,
                'message': f'Event visibility {"enabled" if visible else "disabled"}',
                'current_state': event.display_on_website
            })
            
        except Exception as e:
            print(f"Error in toggle_event_visibility: {str(e)}")  # Debug log
            db.session.rollback()  # Roll back on error
            return jsonify({
                'success': False,
                'message': f'An error occurred: {str(e)}'
            }), 500
