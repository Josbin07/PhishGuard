from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import bcrypt
import uuid
import json

@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

class AdminUser(UserMixin, db.Model):
    __tablename__ = 'admin_users'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(300), nullable=False)
    role          = db.Column(db.String(50), default='admin')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()

    def check_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password_hash.encode())

    def is_admin(self):
        return self.role == 'admin'

class PhishTemplate(db.Model):
    __tablename__ = 'templates'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    slug          = db.Column(db.String(50), unique=True, nullable=False)
    difficulty    = db.Column(db.String(20), default='medium')
    email_subject = db.Column(db.String(200))
    email_body    = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    campaigns     = db.relationship('Campaign', backref='template', lazy=True)

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(150), nullable=False)
    template_id   = db.Column(db.Integer, db.ForeignKey('templates.id'))
    created_by    = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    status        = db.Column(db.String(20), default='active')
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    targets       = db.relationship('Target', backref='campaign', lazy=True, cascade='all, delete')
    creator       = db.relationship('AdminUser', backref='campaigns')

class Target(db.Model):
    __tablename__ = 'targets'
    id             = db.Column(db.Integer, primary_key=True)
    campaign_id    = db.Column(db.Integer, db.ForeignKey('campaigns.id'))
    email          = db.Column(db.String(200), default='')
    tracking_token = db.Column(db.String(64), unique=True, nullable=False,
                               default=lambda: uuid.uuid4().hex)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    events         = db.relationship('Event', backref='target', lazy=True, cascade='all, delete')

class Event(db.Model):
    __tablename__ = 'events'
    id         = db.Column(db.Integer, primary_key=True)
    target_id  = db.Column(db.Integer, db.ForeignKey('targets.id'))
    event_type = db.Column(db.String(50), nullable=False)
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45), default='')
    user_agent = db.Column(db.String(300), default='')

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id        = db.Column(db.Integer, primary_key=True)
    admin_id  = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    action    = db.Column(db.String(200))
    detail    = db.Column(db.Text, default='')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    admin     = db.relationship('AdminUser', backref='audit_logs')

    def save(self):
        db.session.add(self)
        db.session.commit()
