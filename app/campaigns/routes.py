from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import Campaign, Target, PhishTemplate, AuditLog, Event
from app import db, mail
from flask_mail import Message
from docx import Document
import uuid
import io

campaigns_bp = Blueprint('campaigns', __name__)


def extract_emails_from_docx(file_bytes):
    """Read a .docx file and extract all email addresses from it."""
    doc = Document(io.BytesIO(file_bytes))
    emails = []
    for para in doc.paragraphs:
        line = para.text.strip()
        if '@' in line and '.' in line:
            emails.append(line.lower())
    return emails


def send_simulation_email(target, campaign, base_url):
    """Send one simulation email. Returns True on success."""
    tracking_url = f"{base_url}/p/{target.tracking_token}"
    body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto">
      <p>Hi,</p>
      <p>Your account requires immediate verification.
         Please sign in to confirm your identity:</p>
      <p style="text-align:center;margin:30px 0">
        <a href="{tracking_url}"
           style="background:#0067b8;color:white;padding:12px 28px;
                  text-decoration:none;border-radius:4px;font-size:15px">
          Verify Account
        </a>
      </p>
      <p style="color:#888;font-size:12px">
        If you did not request this, you can safely ignore this email.
      </p>
    </div>
    """
    msg = Message(
        subject    = campaign.template.email_subject or 'Action Required: Verify your account',
        recipients = [target.email],
        html       = body
    )
    mail.send(msg)


@campaigns_bp.route('/')
@login_required
def list_campaigns():
    campaigns = Campaign.query.order_by(Campaign.created_at.desc()).all()
    return render_template('campaigns/list.html', campaigns=campaigns)


@campaigns_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_campaign():
    if request.method == 'POST':
        campaign = Campaign(
            name        = request.form['name'],
            template_id = request.form['template_id'],
            created_by  = current_user.id,
            status      = 'active'
        )
        db.session.add(campaign)
        db.session.flush()

        # ── Parse Word file ───────────────────────────────────
        file  = request.files.get('emails_docx')
        added = 0

        if file and file.filename.endswith('.docx'):
            emails = extract_emails_from_docx(file.read())
            for email in emails:
                db.session.add(Target(
                    campaign_id    = campaign.id,
                    email          = email,
                    tracking_token = uuid.uuid4().hex
                ))
                added += 1
        else:
            # No file — single test target
            db.session.add(Target(
                campaign_id    = campaign.id,
                email          = 'test@simulation.local',
                tracking_token = uuid.uuid4().hex
            ))
            added = 1

        db.session.commit()

        # ── Auto-send emails immediately ──────────────────────
        base_url     = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
        sent, failed = 0, 0

        for target in campaign.targets:
            if target.email == 'test@simulation.local':
                continue
            try:
                send_simulation_email(target, campaign, base_url)
                db.session.add(Event(
                    target_id  = target.id,
                    event_type = 'email_sent',
                    ip_address = '',
                    user_agent = ''
                ))
                sent += 1
            except Exception as ex:
                failed += 1
                print(f"[MAIL ERROR] {target.email}: {ex}")

        db.session.commit()

        if sent > 0:
            flash(f'Campaign created! {sent} email(s) sent automatically. {failed} failed.', 'success')
        else:
            flash(f'Campaign created with {added} target(s). Configure SMTP in .env to send emails.', 'info')

        return redirect(url_for('campaigns.view', id=campaign.id))

    templates = PhishTemplate.query.all()
    return render_template('campaigns/new.html', templates=templates)


@campaigns_bp.route('/<int:id>')
@login_required
def view(id):
    campaign = Campaign.query.get_or_404(id)
    base_url = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    target_urls = []
    for t in campaign.targets:
        target_urls.append({
            'email'  : t.email,
            'url'    : f"{base_url}/p/{t.tracking_token}",
            'token'  : t.tracking_token,
            'events' : t.events
        })
    return render_template('campaigns/view.html',
                           campaign=campaign,
                           target_urls=target_urls,
                           base_url=base_url)


@campaigns_bp.route('/<int:id>/send', methods=['POST'])
@login_required
def send_emails(id):
    """Manual resend button."""
    campaign     = Campaign.query.get_or_404(id)
    base_url     = current_app.config.get('APP_BASE_URL', 'http://localhost:5000')
    sent, failed = 0, 0

    for target in campaign.targets:
        if target.email == 'test@simulation.local':
            continue
        try:
            send_simulation_email(target, campaign, base_url)
            db.session.add(Event(
                target_id  = target.id,
                event_type = 'email_sent',
                ip_address = '',
                user_agent = ''
            ))
            sent += 1
        except Exception as ex:
            failed += 1
            print(f"[MAIL ERROR] {target.email}: {ex}")

    db.session.commit()
    flash(f'Resent: {sent} sent, {failed} failed.', 'success' if failed == 0 else 'warning')
    return redirect(url_for('campaigns.view', id=id))


@campaigns_bp.route('/<int:id>/pause', methods=['POST'])
@login_required
def pause(id):
    c = Campaign.query.get_or_404(id)
    c.status = 'paused'
    db.session.commit()
    flash('Campaign paused.', 'warning')
    return redirect(url_for('campaigns.view', id=id))


@campaigns_bp.route('/<int:id>/resume', methods=['POST'])
@login_required
def resume(id):
    c = Campaign.query.get_or_404(id)
    c.status = 'active'
    db.session.commit()
    flash('Campaign resumed.', 'success')
    return redirect(url_for('campaigns.view', id=id))


@campaigns_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    c = Campaign.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash('Campaign deleted.', 'info')
    return redirect(url_for('campaigns.list_campaigns'))
