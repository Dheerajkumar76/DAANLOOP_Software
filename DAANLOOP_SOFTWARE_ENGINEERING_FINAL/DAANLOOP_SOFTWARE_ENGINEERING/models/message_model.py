"""Message Model - CRUD operations for messages table."""
from database import get_db, close_db


# Fixed preset messages a sender can pick from
PRESET_MESSAGES = [
    "Is this item still available?",
    "I'm interested, how do I collect it?",
    "Can you hold this item for me?",
    "What is the exact pickup location?",
    "Is the condition as described?",
    "Can I see more photos of this item?",
    "When would be a good time to pick up?",
]

# Fixed preset replies an owner can pick from
PRESET_REPLIES = [
    "Yes, it's still available!",
    "Sorry, this item has been claimed.",
    "Sure, I can hold it for 2 days.",
    "Please contact me on the number listed.",
    "Yes, the condition is exactly as described.",
    "I can share more photos, please share your contact.",
    "Anytime between 10 AM - 6 PM works for me.",
    "Please come to the location mentioned in the listing.",
]


def send_message(sender_id, receiver_id, listing_id, message_text):
    db = get_db()
    try:
        db.execute(
            '''INSERT INTO messages (sender_id, receiver_id, listing_id, message_text)
               VALUES (?, ?, ?, ?)''',
            (sender_id, receiver_id, listing_id, message_text)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def reply_to_message(message_id, reply_text):
    db = get_db()
    try:
        db.execute(
            "UPDATE messages SET reply_text = ?, replied_at = CURRENT_TIMESTAMP WHERE id = ?",
            (reply_text, message_id)
        )
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        close_db(db)


def get_inbox(user_id):
    """Get all messages received by this user (as listing owner)."""
    db = get_db()
    rows = db.execute('''
        SELECT m.*, u.username as sender_name, l.title as listing_title
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        JOIN listings l ON m.listing_id = l.id
        WHERE m.receiver_id = ?
        ORDER BY m.created_at DESC
    ''', (user_id,)).fetchall()
    close_db(db)
    return rows


def get_sent_messages(user_id):
    """Get all messages sent by this user."""
    db = get_db()
    rows = db.execute('''
        SELECT m.*, u.username as receiver_name, l.title as listing_title
        FROM messages m
        JOIN users u ON m.receiver_id = u.id
        JOIN listings l ON m.listing_id = l.id
        WHERE m.sender_id = ?
        ORDER BY m.created_at DESC
    ''', (user_id,)).fetchall()
    close_db(db)
    return rows


def get_message_by_id(message_id):
    db = get_db()
    row = db.execute('''
        SELECT m.*,
               s.username as sender_name,
               r.username as receiver_name,
               l.title as listing_title
        FROM messages m
        JOIN users s ON m.sender_id = s.id
        JOIN users r ON m.receiver_id = r.id
        JOIN listings l ON m.listing_id = l.id
        WHERE m.id = ?
    ''', (message_id,)).fetchone()
    close_db(db)
    return row


def mark_as_read(message_id):
    db = get_db()
    try:
        db.execute("UPDATE messages SET is_read = 1 WHERE id = ?", (message_id,))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        close_db(db)


def count_unread(user_id):
    db = get_db()
    result = db.execute(
        "SELECT COUNT(*) as cnt FROM messages WHERE receiver_id = ? AND is_read = 0",
        (user_id,)
    ).fetchone()
    close_db(db)
    return result['cnt']


def get_messages_for_listing(listing_id, user_id):
    """Get conversation between a user and listing owner for a specific listing."""
    db = get_db()
    rows = db.execute('''
        SELECT m.*, s.username as sender_name, r.username as receiver_name
        FROM messages m
        JOIN users s ON m.sender_id = s.id
        JOIN users r ON m.receiver_id = r.id
        WHERE m.listing_id = ? AND (m.sender_id = ? OR m.receiver_id = ?)
        ORDER BY m.created_at ASC
    ''', (listing_id, user_id, user_id)).fetchall()
    close_db(db)
    return rows
