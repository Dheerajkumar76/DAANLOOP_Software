"""
Sprint 3 - Messages Blueprint
Handles: Send preset messages to listing owners, reply with preset replies, inbox
"""
from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from models.message_model import (
    send_message, reply_to_message, get_inbox, get_sent_messages,
    get_message_by_id, mark_as_read, PRESET_MESSAGES, PRESET_REPLIES
)
from models.listing_model import get_listing_by_id
from utils.security import login_required

messages_bp = Blueprint('sprint3_messages', __name__, template_folder='templates')


@messages_bp.route('/messages')
@login_required
def inbox():
    tab = request.args.get('tab', 'received')
    received = get_inbox(session['user_id'])
    sent = get_sent_messages(session['user_id'])
    return render_template('sprint3/inbox.html',
        received=received, sent=sent, tab=tab,
        preset_replies=PRESET_REPLIES)


@messages_bp.route('/messages/send/<int:listing_id>', methods=['POST'])
@login_required
def send(listing_id):
    listing = get_listing_by_id(listing_id)
    if not listing:
        flash('Listing not found.', 'warning')
        return redirect(url_for('sprint1_listings.browse'))

    if listing['owner_id'] == session['user_id']:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))

    message_text = request.form.get('message_text', '').strip()

    # Validate: must be one of the preset messages
    if message_text not in PRESET_MESSAGES:
        flash('Please select a valid message.', 'danger')
        return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))

    if send_message(session['user_id'], listing['owner_id'], listing_id, message_text):
        flash('Message sent to the listing owner!', 'success')
    else:
        flash('Failed to send message.', 'danger')

    return redirect(url_for('sprint1_listings.view_listing', listing_id=listing_id))


@messages_bp.route('/messages/reply/<int:message_id>', methods=['POST'])
@login_required
def reply(message_id):
    msg = get_message_by_id(message_id)
    if not msg:
        flash('Message not found.', 'warning')
        return redirect(url_for('sprint3_messages.inbox'))

    # Only the receiver (listing owner) can reply
    if msg['receiver_id'] != session['user_id']:
        flash('You can only reply to messages sent to you.', 'danger')
        return redirect(url_for('sprint3_messages.inbox'))

    reply_text = request.form.get('reply_text', '').strip()

    # Validate: must be one of the preset replies
    if reply_text not in PRESET_REPLIES:
        flash('Please select a valid reply.', 'danger')
        return redirect(url_for('sprint3_messages.inbox'))

    if reply_to_message(message_id, reply_text):
        flash('Reply sent!', 'success')
    else:
        flash('Failed to send reply.', 'danger')

    return redirect(url_for('sprint3_messages.inbox'))


@messages_bp.route('/messages/<int:message_id>/read')
@login_required
def read_message(message_id):
    msg = get_message_by_id(message_id)
    if not msg:
        flash('Message not found.', 'warning')
        return redirect(url_for('sprint3_messages.inbox'))

    # Only sender or receiver can view
    if msg['sender_id'] != session['user_id'] and msg['receiver_id'] != session['user_id']:
        flash('Access denied.', 'danger')
        return redirect(url_for('sprint3_messages.inbox'))

    # Mark as read if receiver is viewing
    if msg['receiver_id'] == session['user_id'] and not msg['is_read']:
        mark_as_read(message_id)

    return render_template('sprint3/view_message.html', msg=msg, preset_replies=PRESET_REPLIES)
