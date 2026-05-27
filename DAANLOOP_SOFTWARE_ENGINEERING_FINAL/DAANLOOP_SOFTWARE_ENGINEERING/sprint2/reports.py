"""
Sprint 2 - Reports Blueprint
Handles: Report listings, Admin review reports
"""
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.report_model import create_report, get_all_reports, update_report_status, has_reported
from models.listing_model import get_listing_by_id, soft_delete_listing
from utils.security import login_required, admin_required

reports_bp = Blueprint('sprint2_reports', __name__, template_folder='templates')


@reports_bp.route('/report/<int:listing_id>', methods=['POST'])
@login_required
def report_listing(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    if listing['owner_id'] == session['user_id']:
        flash('You cannot report your own listing.', 'warning')
        return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))

    if has_reported(session['user_id'], listing_id):
        flash('You have already reported this listing.', 'info')
        return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))

    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Please provide a reason for the report.', 'danger')
        return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))

    if create_report(session['user_id'], listing_id, reason):
        # Log activity
        try:
            from models.activity_model import log_activity
            log_activity(session['user_id'], 'report_listing', f'Reported listing: {listing["title"]}')
        except Exception:
            pass
        flash('Report submitted. An admin will review it.', 'success')
    else:
        flash('Failed to submit report.', 'danger')

    return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))


@reports_bp.route('/admin/reports')
@admin_required
def admin_reports():
    status_filter = request.args.get('status', 'pending')
    reports = get_all_reports(status=status_filter if status_filter != 'all' else None)
    return render_template('sprint2/admin_reports.html', reports=reports, status_filter=status_filter)


@reports_bp.route('/admin/report/<int:report_id>/review', methods=['POST'])
@admin_required
def review_report(report_id):
    action = request.form.get('action', '')
    if action == 'soft_delete':
        listing_id = request.form.get('listing_id', 0, type=int)
        soft_delete_listing(listing_id)
        update_report_status(report_id, 'reviewed')
        flash('Listing soft-deleted and report marked as reviewed.', 'success')
    elif action == 'dismiss':
        update_report_status(report_id, 'dismissed')
        flash('Report dismissed.', 'info')
    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('sprint2_reports.admin_reports'))
