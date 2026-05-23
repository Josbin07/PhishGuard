from flask import Blueprint, render_template, request
from app.models import Target, Event
from app import db

training_bp = Blueprint('training', __name__)

@training_bp.route('/awareness/<token>')
def awareness(token):
    target = Target.query.filter_by(tracking_token=token).first_or_404()
    db.session.add(Event(
        target_id  = target.id,
        event_type = 'training_shown',
        ip_address = request.remote_addr or '',
        user_agent = request.headers.get('User-Agent', '')[:300]
    ))
    db.session.commit()
    return render_template('training/awareness.html')
