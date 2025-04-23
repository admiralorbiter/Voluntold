from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
from models import db
from enum import IntEnum
import secrets

class SecurityLevel(IntEnum):
    """
    Enum for user security levels. Using IntEnum ensures values are stored as integers in the database.
    Higher numbers indicate more privileges.
    """
    USER = 0        # Regular user with basic access
    SUPERVISOR = 1  # Can supervise regular users
    MANAGER = 2     # Can manage supervisors and users
    ADMIN = 3       # Full system access

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    security_level = db.Column(db.Integer, default=SecurityLevel.USER, nullable=False)
    
    # API Authentication
    api_token = db.Column(db.String(64), unique=True, index=True)
    token_expiry = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                           onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a new user instance.
        The is_admin parameter is a convenience flag that sets the security level.
        """
        # Set timestamps if not provided
        now = datetime.now(timezone.utc)
        if 'created_at' not in kwargs:
            kwargs['created_at'] = now
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = now
            
        is_admin_value = kwargs.pop('is_admin', False)  # Extract is_admin before super().__init__
        super().__init__(**kwargs)
        if 'security_level' not in kwargs:
            self.is_admin = is_admin_value  # Use the setter to set security_level

    @property
    def is_admin(self):
        """Property to check if user is an admin"""
        return self.security_level == SecurityLevel.ADMIN

    @is_admin.setter
    def is_admin(self, value):
        """Setter for is_admin property"""
        self.security_level = SecurityLevel.ADMIN if value else SecurityLevel.USER

    def has_permission_level(self, required_level):
        """Check if user has required security level or higher"""
        return self.security_level >= required_level

    def can_manage_user(self, other_user):
        """Check if user can manage another user based on security level"""
        return self.security_level > other_user.security_level

    @classmethod
    def find_by_username_or_email(cls, login):
        """Find a user by either username or email"""
        return cls.query.filter(
            db.or_(
                cls.username == login,
                cls.email == login
            )
        ).first()

    def generate_api_token(self, expiration=30):
        """Generate a secure API token for this user"""
        token = secrets.token_hex(32)  # 64 characters hex string
        self.api_token = token
        self.token_expiry = datetime.now(timezone.utc) + timedelta(days=expiration)
        db.session.commit()
        return token
    
    def check_api_token(self, token):
        """Check if the provided token is valid for this user"""
        if not self.api_token or not self.token_expiry:
            return False
        
        if self.api_token != token:
            return False
            
        # Convert token_expiry to UTC if it's naive
        if self.token_expiry.tzinfo is None:
            self.token_expiry = self.token_expiry.replace(tzinfo=timezone.utc)

        if datetime.now(timezone.utc) > self.token_expiry:
            return False
            
        return True
        
    def revoke_api_token(self):
        """Revoke the current API token"""
        self.api_token = None
        self.token_expiry = None
        db.session.commit()
    
    @classmethod
    def find_by_api_token(cls, token):
        """Find a user by their API token"""
        return cls.query.filter_by(api_token=token).first()
    
    def to_dict(self):
        """Convert user object to dictionary for API responses"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'security_level': self.security_level,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __str__(self):
        """String representation of the user"""
        return f"<User {self.username}>"

    def __repr__(self):
        """Developer representation of the user"""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', security_level={self.security_level})>" 