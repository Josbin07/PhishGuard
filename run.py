from app import create_app, db
from app.models import AdminUser, PhishTemplate

app = create_app()

with app.app_context():
    db.create_all()

    if not AdminUser.query.filter_by(email='admin@phishguard.local').first():
        admin = AdminUser(name='Admin', email='admin@phishguard.local', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    if not PhishTemplate.query.filter_by(slug='ms365').first():
        t = PhishTemplate(
            name='Microsoft 365 Login',
            slug='ms365',
            difficulty='medium',
            email_subject='Action Required: Verify your account'
        )
        db.session.add(t)

    db.session.commit()
    print("✅ Database ready. Admin: admin@phishguard.local / admin123")

if __name__ == '__main__':
    app.run(debug=True)
