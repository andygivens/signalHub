import logging
from email.message import EmailMessage
from typing import Dict, Any
from .config import get_pushover_config
from .settings_bridge import get_setting

def handle_email(message: EmailMessage, config: Dict[str, Any]):
    """Process incoming email and send notifications"""
    
    # Get current Pushover settings from database
    pushover_config = get_pushover_config()
    
    if not pushover_config.get('token'):
        logging.warning("No Pushover token configured - skipping notification")
        return
    
    # Extract email details
    sender = message.get('From', 'Unknown')
    subject = message.get('Subject', 'No Subject') 
    recipient = message.get('To', '')
    
    # Create notification message
    notification_text = f"From: {sender}\nSubject: {subject}"
    
    # Send notification using current settings
    send_pushover_notification(
        token=pushover_config['token'],
        user=pushover_config.get('user'),
        device=pushover_config.get('device'),
        message=notification_text,
        title=f"Email Alert: {subject[:50]}"
    )

def send_pushover_notification(token: str, user: str, device: str = None, 
                             message: str = "", title: str = "SignalHub Alert"):
    """Send notification via Pushover API using current settings"""
    import requests
    
    if not token or not user:
        logging.error("Pushover token and user are required")
        return False
    
    data = {
        'token': token,
        'user': user,
        'message': message,
        'title': title,
    }
    
    if device:
        data['device'] = device
    
    try:
        response = requests.post('https://api.pushover.net/1/messages.json', data=data)
        if response.status_code == 200:
            logging.info(f"Notification sent successfully: {title}")
            return True
        else:
            logging.error(f"Pushover API error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logging.error(f"Failed to send Pushover notification: {e}")
        return False