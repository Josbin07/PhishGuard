from flask import Blueprint, Response, render_template
from flask_login import login_required
from app.models import Campaign
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, Image)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io

reports_bp = Blueprint('reports', __name__)

# ── Colors ────────────────────────────────────────────────────
DARK      = colors.HexColor('#1a1a2e')
BLUE      = colors.HexColor('#0067b8')
ACCENT    = colors.HexColor('#f5a623')
LIGHT_BG  = colors.HexColor('#f0f4f8')
WHITE     = colors.white
RED       = colors.HexColor('#dc3545')
GREEN     = colors.HexColor('#28a745')
ORANGE    = colors.HexColor('#fd7e14')
GREY      = colors.HexColor('#6c757d')
YELLOW    = colors.HexColor('#ffc107')


def build_rows(campaign):
    rows = []
    for target in campaign.targets:
        for e in sorted(target.events, key=lambda x: x.timestamp):
            rows.append({
                'email'    : target.email,
                'event'    : e.event_type,
                'timestamp': e.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'ip'       : e.ip_address or '—',
                'ua'       : (e.user_agent or '—')[:60]
            })
    return rows


def get_target_summary(campaign):
    """Per-target summary: who clicked, who completed training."""
    summary = []
    for target in campaign.targets:
        if target.email == 'test@simulation.local':
            continue
        events      = [e.event_type for e in target.events]
        clicked     = 'link_clicked' in events
        submitted   = 'credentials_submitted' in events
        trained     = 'training_shown' in events
        email_sent  = 'email_sent' in events
        summary.append({
            'email'     : target.email,
            'email_sent': email_sent,
            'clicked'   : clicked,
            'submitted' : submitted,
            'trained'   : trained,
        })
    return summary


def make_bar_chart(summary):
    """Bar chart — sent vs clicked vs trained."""
    sent    = sum(1 for r in summary if r['email_sent'])
    clicked = sum(1 for r in summary if r['clicked'])
    trained = sum(1 for r in summary if r['trained'])

    fig, ax = plt.subplots(figsize=(6, 3))
    bars    = ax.bar(
        ['Emails Sent', 'Links Clicked', 'Training Completed'],
        [sent, clicked, trained],
        color   = ['#0067b8', '#fd7e14', '#28a745'],
        width   = 0.5,
        zorder  = 2
    )
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.yaxis.grid(True, color='#dddddd', zorder=1)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel('Count', fontsize=9)
    ax.set_title('Campaign Overview', fontsize=11, fontweight='bold', pad=10)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.1,
                str(int(h)), ha='center', va='bottom', fontsize=9, fontweight='bold')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def make_pie_chart(summary):
    """Pie chart — clicked vs not clicked."""
    clicked     = sum(1 for r in summary if r['clicked'])
    not_clicked = sum(1 for r in summary if not r['clicked'] and r['email_sent'])
    total       = clicked + not_clicked

    if total == 0:
        return None

    fig, ax = plt.subplots(figsize=(4, 3))
    wedge_props = {'linewidth': 2, 'edgecolor': 'white'}
    ax.pie(
        [clicked, not_clicked],
        labels      = [f'Clicked ({clicked})', f'Did Not Click ({not_clicked})'],
        colors      = ['#fd7e14', '#28a745'],
        autopct     = '%1.1f%%',
        startangle  = 90,
        wedgeprops  = wedge_props,
        textprops   = {'fontsize': 9}
    )
    ax.set_title('Click Distribution', fontsize=11, fontweight='bold', pad=10)
    fig.patch.set_facecolor('#ffffff')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_pdf(campaign):
    summary  = get_target_summary(campaign)
    buffer   = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize     = A4,
        rightMargin  = 2*cm,
        leftMargin   = 2*cm,
        topMargin    = 2*cm,
        bottomMargin = 2*cm,
        title        = f"PhishGuard Report — {campaign.name}"
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Paragraph Styles ──────────────────────────────────────
    section_style = ParagraphStyle('Section',
        fontSize=12, textColor=DARK, fontName='Helvetica-Bold',
        spaceBefore=14, spaceAfter=5)

    body_style = ParagraphStyle('Body',
        fontSize=9, textColor=colors.HexColor('#333333'),
        fontName='Helvetica', spaceAfter=4, leading=14)

    small_style = ParagraphStyle('Small',
        fontSize=8, textColor=GREY, fontName='Helvetica', leading=11)

    center_style = ParagraphStyle('Center',
        fontSize=9, fontName='Helvetica', alignment=TA_CENTER)

    # ══════════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════════
    header_data = [[
        Paragraph('<font color="white" size="18"><b>🎧 PhishGuard</b></font>',
                  ParagraphStyle('H', fontSize=18, textColor=WHITE,
                                 fontName='Helvetica-Bold')),
        Paragraph(
            '<font color="#aaccee" size="9">Security Awareness Campaign Report</font><br/>'
            f'<font color="#cccccc" size="8">Generated: {datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")}</font>',
            ParagraphStyle('HS', fontSize=9, textColor=WHITE,
                           fontName='Helvetica', alignment=TA_RIGHT, leading=14))
    ]]
    header_tbl = Table(header_data, colWidths=[9*cm, 8*cm])
    header_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('PADDING',    (0,0), (-1,-1), 18),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(header_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ══════════════════════════════════════════════════════════
    # CAMPAIGN DETAILS
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph('Campaign Details', section_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE, spaceAfter=6))

    info_data = [
        ['Campaign Name',      campaign.name],
        ['Phishing Template',  campaign.template.name],
        ['Status',             campaign.status.upper()],
        ['Date Created',       campaign.created_at.strftime('%B %d, %Y at %H:%M')],
        ['Total Targets',      str(len(summary))],
    ]
    info_tbl = Table(info_data, colWidths=[5*cm, 12*cm])
    info_tbl.setStyle(TableStyle([
        ('FONTNAME',     (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME',     (1,0), (1,-1), 'Helvetica'),
        ('FONTSIZE',     (0,0), (-1,-1), 9),
        ('PADDING',      (0,0), (-1,-1), 7),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, WHITE]),
        ('GRID',         (0,0), (-1,-1), 0.4, colors.HexColor('#dddddd')),
        ('TEXTCOLOR',    (0,0), (0,-1), DARK),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ══════════════════════════════════════════════════════════
    # STATISTICS SUMMARY
    # ══════════════════════════════════════════════════════════
    sent_c     = sum(1 for r in summary if r['email_sent'])
    clicked_c  = sum(1 for r in summary if r['clicked'])
    trained_c  = sum(1 for r in summary if r['trained'])
    safe_c     = sum(1 for r in summary if not r['clicked'] and r['email_sent'])
    click_rate = round((clicked_c / sent_c * 100), 1) if sent_c > 0 else 0
    train_rate = round((trained_c / clicked_c * 100), 1) if clicked_c > 0 else 0

    story.append(Paragraph('Executive Summary', section_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE, spaceAfter=6))

    def stat_cell(number, label, hex_color):
        return Paragraph(
            f'<font size="20" color="{hex_color}"><b>{number}</b></font><br/>'
            f'<font size="8" color="#555555">{label}</font>',
            ParagraphStyle('SC', alignment=TA_CENTER, leading=22, fontName='Helvetica'))

    stats_data = [[
        stat_cell(sent_c,    'Emails Sent',   '#0067b8'),
        stat_cell(clicked_c, 'Links Clicked', '#fd7e14'),
        stat_cell(safe_c,    'Did Not Click', '#28a745'),
        stat_cell(trained_c, 'Training Done', '#6f42c1'),
        stat_cell(f'{click_rate}%', 'Click Rate', '#dc3545'),
    ]]
    stats_tbl = Table(stats_data, colWidths=[3.4*cm]*5)
    stats_tbl.setStyle(TableStyle([
        ('ALIGN',      (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('PADDING',    (0,0), (-1,-1), 12),
        ('GRID',       (0,0), (-1,-1), 0.4, colors.HexColor('#dddddd')),
    ]))
    story.append(stats_tbl)
    story.append(Spacer(1, 0.3*cm))

    # Risk badge
    if click_rate >= 50:
        risk, risk_bg, risk_note = 'HIGH RISK', colors.HexColor('#fde8e8'), \
            'Over half of recipients clicked the phishing link. Immediate mandatory training is recommended.'
    elif click_rate >= 20:
        risk, risk_bg, risk_note = 'MEDIUM RISK', colors.HexColor('#fff3cd'), \
            'A notable portion clicked the link. Targeted awareness sessions are advised.'
    else:
        risk, risk_bg, risk_note = 'LOW RISK', colors.HexColor('#d4edda'), \
            'Few recipients clicked the link. Maintain regular awareness programs.'

    risk_data = [[
        Paragraph(f'<b>Risk Assessment: {risk}</b>',
                  ParagraphStyle('RH', fontSize=9, fontName='Helvetica-Bold', textColor=DARK)),
        Paragraph(risk_note, small_style)
    ]]
    risk_tbl = Table(risk_data, colWidths=[4.5*cm, 12.5*cm])
    risk_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), risk_bg),
        ('PADDING',    (0,0), (-1,-1), 10),
        ('GRID',       (0,0), (-1,-1), 0.5, ACCENT),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(risk_tbl)
    story.append(Spacer(1, 0.5*cm))

    # ══════════════════════════════════════════════════════════
    # GRAPHS
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph('Visual Analytics', section_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE, spaceAfter=8))

    bar_buf = make_bar_chart(summary)
    pie_buf = make_pie_chart(summary)

    if bar_buf and pie_buf:
        bar_img = Image(bar_buf, width=10*cm, height=5*cm)
        pie_img = Image(pie_buf, width=7*cm,  height=5*cm)
        chart_data = [[bar_img, pie_img]]
        chart_tbl  = Table(chart_data, colWidths=[10.5*cm, 7.5*cm])
        chart_tbl.setStyle(TableStyle([
            ('ALIGN',   (0,0), (-1,-1), 'CENTER'),
            ('VALIGN',  (0,0), (-1,-1), 'MIDDLE'),
            ('PADDING', (0,0), (-1,-1), 6),
            ('BOX',     (0,0), (-1,-1), 0.4, colors.HexColor('#dddddd')),
            ('BACKGROUND', (0,0), (-1,-1), WHITE),
        ]))
        story.append(chart_tbl)
    elif bar_buf:
        story.append(Image(bar_buf, width=14*cm, height=6*cm))

    story.append(Spacer(1, 0.5*cm))

    # ══════════════════════════════════════════════════════════
    # WHO CLICKED — detailed table
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph('Who Clicked the Link', section_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE, spaceAfter=6))

    clicked_targets = [r for r in summary if r['clicked']]

    if clicked_targets:
        click_data = [['#', 'Email Address', 'Link Clicked', 'Training Completed']]
        for i, r in enumerate(clicked_targets, 1):
            click_data.append([
                Paragraph(str(i), small_style),
                Paragraph(r['email'], small_style),
                Paragraph('<font color="#fd7e14"><b>✓ Yes</b></font>',
                          ParagraphStyle('Y', fontSize=8, fontName='Helvetica-Bold',
                                         alignment=TA_CENTER)),
                Paragraph(
                    '<font color="#28a745"><b>✓ Trained</b></font>'
                    if r['trained'] else
                    '<font color="#dc3545"><b>✗ Not Yet</b></font>',
                    ParagraphStyle('T', fontSize=8, fontName='Helvetica-Bold',
                                   alignment=TA_CENTER))
            ])

        click_tbl = Table(click_data, colWidths=[1*cm, 9*cm, 3.5*cm, 3.5*cm])
        click_tbl.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0), DARK),
            ('TEXTCOLOR',      (0,0), (-1,0), WHITE),
            ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0,0), (-1,0), 8),
            ('ALIGN',          (0,0), (-1,0), 'CENTER'),
            ('PADDING',        (0,0), (-1,-1), 7),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, LIGHT_BG]),
            ('GRID',           (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',          (2,1), (-1,-1), 'CENTER'),
        ]))
        story.append(click_tbl)
    else:
        story.append(Paragraph(
            'No recipients clicked the phishing link. Excellent awareness level!',
            ParagraphStyle('Good', fontSize=9, textColor=GREEN,
                           fontName='Helvetica-Bold')))

    story.append(Spacer(1, 0.5*cm))

    # ══════════════════════════════════════════════════════════
    # WHO DID NOT CLICK
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph('Who Did Not Click', section_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE, spaceAfter=6))

    safe_targets = [r for r in summary if not r['clicked'] and r['email_sent']]

    if safe_targets:
        safe_data = [['#', 'Email Address', 'Status']]
        for i, r in enumerate(safe_targets, 1):
            safe_data.append([
                Paragraph(str(i), small_style),
                Paragraph(r['email'], small_style),
                Paragraph('<font color="#28a745"><b>✓ Resisted Phishing</b></font>',
                          ParagraphStyle('S', fontSize=8, fontName='Helvetica-Bold',
                                         alignment=TA_CENTER))
            ])
        safe_tbl = Table(safe_data, colWidths=[1*cm, 12*cm, 4*cm])
        safe_tbl.setStyle(TableStyle([
            ('BACKGROUND',     (0,0), (-1,0), colors.HexColor('#155724')),
            ('TEXTCOLOR',      (0,0), (-1,0), WHITE),
            ('FONTNAME',       (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',       (0,0), (-1,0), 8),
            ('ALIGN',          (0,0), (-1,0), 'CENTER'),
            ('PADDING',        (0,0), (-1,-1), 7),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, colors.HexColor('#f0fff4')]),
            ('GRID',           (0,0), (-1,-1), 0.3, colors.HexColor('#cccccc')),
            ('VALIGN',         (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN',          (2,1), (-1,-1), 'CENTER'),
        ]))
        story.append(safe_tbl)
    else:
        story.append(Paragraph('All recipients clicked the link.', body_style))

    story.append(Spacer(1, 0.8*cm))

    # ══════════════════════════════════════════════════════════
    # RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph('Recommendations', section_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=BLUE, spaceAfter=6))

    recs = []
    if click_rate >= 50:
        recs = [
            'Conduct mandatory phishing awareness training for all staff immediately.',
            'Schedule monthly simulations to measure improvement over time.',
            'Consider a dedicated cybersecurity awareness program.',
            'Enforce multi-factor authentication (MFA) across all accounts.',
        ]
    elif click_rate >= 20:
        recs = [
            'Target training to employees who clicked the simulation link.',
            'Run a follow-up simulation within 60 days to measure progress.',
            'Share phishing tips in team meetings or internal newsletters.',
            'Ensure MFA is enabled for all critical systems.',
        ]
    else:
        recs = [
            'Maintain current awareness training schedule.',
            'Continue quarterly simulations to sustain vigilance.',
            'Reward and acknowledge teams with zero click rates.',
            'Share results with management to demonstrate security posture.',
        ]

    rec_data = [[
        Paragraph(f'{i+1}.  {rec}', body_style)
    ] for i, rec in enumerate(recs)]
    rec_tbl = Table(rec_data, colWidths=[17*cm])
    rec_tbl.setStyle(TableStyle([
        ('BACKGROUND',     (0,0), (-1,-1), LIGHT_BG),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [LIGHT_BG, WHITE]),
        ('PADDING',        (0,0), (-1,-1), 8),
        ('GRID',           (0,0), (-1,-1), 0.3, colors.HexColor('#dddddd')),
    ]))
    story.append(rec_tbl)
    story.append(Spacer(1, 0.8*cm))

    # ══════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════
    footer_data = [[
        Paragraph(
            '<font color="white"><b>PhishGuard</b> — Security Awareness Platform &nbsp;|&nbsp; '
            'Confidential — Internal Use Only</font>',
            ParagraphStyle('F', fontSize=8, textColor=WHITE,
                           fontName='Helvetica', alignment=TA_CENTER))
    ]]
    footer_tbl = Table(footer_data, colWidths=[17*cm])
    footer_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK),
        ('PADDING',    (0,0), (-1,-1), 10),
    ]))
    story.append(footer_tbl)

    doc.build(story)
    buffer.seek(0)
    return buffer


@reports_bp.route('/campaigns/<int:id>/report')
@login_required
def view_report(id):
    campaign   = Campaign.query.get_or_404(id)
    summary    = get_target_summary(campaign)
    sent_c     = sum(1 for r in summary if r['email_sent'])
    clicked_c  = sum(1 for r in summary if r['clicked'])
    trained_c  = sum(1 for r in summary if r['trained'])
    safe_c     = sum(1 for r in summary if not r['clicked'] and r['email_sent'])
    click_rate = round((clicked_c / sent_c * 100), 1) if sent_c > 0 else 0

    return render_template('reports/report.html',
                           campaign=campaign, summary=summary,
                           sent_c=sent_c, clicked_c=clicked_c,
                           trained_c=trained_c, safe_c=safe_c,
                           click_rate=click_rate)


@reports_bp.route('/campaigns/<int:id>/report/download')
@login_required
def download_report(id):
    campaign = Campaign.query.get_or_404(id)
    buffer   = generate_pdf(campaign)
    filename = f"PhishGuard_{campaign.name.replace(' ', '_')}_Report.pdf"
    return Response(
        buffer.getvalue(),
        mimetype = 'application/pdf',
        headers  = {'Content-Disposition': f'attachment; filename={filename}'}
    )
