from flask import flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import login_required, login_user, logout_user
import requests
from forms import LoginForm
from models import User, db
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
        return render_template('dashboard.html')
    
    @app.route('/events')
    def get_events():
        try:
            # Add debug logging
            print(f"Attempting to connect with: {Config.SF_USERNAME}")
            
            sf = Salesforce(
                username=Config.SF_USERNAME,
                password=Config.SF_PASSWORD,
                security_token=Config.SF_SECURITY_TOKEN,
                domain='login'  # Try explicitly setting the domain
            )

            query = "SELECT Id, Name, Volunteers_Needed__c FROM Event__c"
            result = sf.query(query)
            events = result.get('records', [])

            return jsonify(events)

        except SalesforceAuthenticationFailed as e:
            # Enhanced error details
            error_details = {
                'error': 'Salesforce authentication failed',
                'message': str(e),
                'error_code': getattr(e, 'code', None),
                'error_description': getattr(e, 'message', str(e)),
                'status_code': getattr(e, 'status', None),
                # Add a check for credentials (masking sensitive info)
                'credentials_check': {
                    'username_provided': bool(Config.SF_USERNAME),
                    'password_provided': bool(Config.SF_PASSWORD),
                    'security_token_provided': bool(Config.SF_SECURITY_TOKEN),
                    'username_length': len(Config.SF_USERNAME) if Config.SF_USERNAME else 0,
                    'security_token_length': len(Config.SF_SECURITY_TOKEN) if Config.SF_SECURITY_TOKEN else 0
                }
            }
            print("Authentication Error Details:", error_details)  # Server-side logging
            return jsonify(error_details), 401

        except Exception as e:
            error_details = {
                'error': 'Unexpected error',
                'message': str(e),
                'type': type(e).__name__
            }
            print("Unexpected Error:", error_details)  # Server-side logging
            return jsonify(error_details), 500
