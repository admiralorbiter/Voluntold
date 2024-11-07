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
    def dashboard():
        # Get initial events from database and convert to dict
        events = [event.to_dict() for event in Session.query.all()]
        return render_template('dashboard.html', initial_events=events)
    
    @app.route('/events')
    def get_events():
        try:
            print(f"Attempting to connect with: {Config.SF_USERNAME}")
            
            sf = Salesforce(
                username=Config.SF_USERNAME,
                password=Config.SF_PASSWORD,
                security_token=Config.SF_SECURITY_TOKEN,
                domain='login'
            )

            query = "SELECT Id, Name, Available_slots__c, Filled_Volunteer_Jobs__c, Date_and_Time_for_Cal__c, Session_Type__c, Registration_Link__c, Display_on_Website__c FROM Session__c WHERE Start_Date__c > TODAY and Available_Slots__c>0"
            result = sf.query(query)
            events = result.get('records', [])

            # Store the data
            new_count, updated_count = Session.upsert_from_salesforce(events)
            
            # Get updated events from database
            updated_events = Session.query.all()
            
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
