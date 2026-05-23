from flask import Blueprint, request, redirect, url_for, render_template, Response
from app.models import Target, Event
from app import db

tracker_bp = Blueprint('tracker', __name__)

def log_event(target_id, event_type):
    db.session.add(Event(
        target_id  = target_id,
        event_type = event_type,
        ip_address = request.remote_addr or '',
        user_agent = request.headers.get('User-Agent', '')[:300]
    ))
    db.session.commit()

@tracker_bp.route('/p/<token>')
def landing(token):
    target = Target.query.filter_by(tracking_token=token).first_or_404()
    log_event(target.id, 'link_clicked')
    slug = target.campaign.template.slug
    return render_template(f'lures/{slug}.html', token=token)

@tracker_bp.route('/submit/<token>', methods=['POST'])
def submit(token):
    target = Target.query.filter_by(tracking_token=token).first_or_404()
    log_event(target.id, 'credentials_submitted')
    # form data is never read or stored
    return redirect(url_for('training.awareness', token=token))
