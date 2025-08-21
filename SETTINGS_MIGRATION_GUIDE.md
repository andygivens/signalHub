# Example modifications for your existing signalhub code
# This shows how to update your original code to use database settings

# In your SMTP handler (wherever you send emails):
"""
OLD CODE:
import os
smtp_host = os.getenv('SMTP_HOST', 'localhost')
smtp_port = int(os.getenv('SMTP_PORT', '587'))

NEW CODE:
from .settings_bridge import get_smtp_config
smtp_config = get_smtp_config()
smtp_host = smtp_config['host']
smtp_port = smtp_config['port']
"""

# In your Pushover handler:
"""
OLD CODE:
import os
pushover_token = os.getenv('PUSHOVER_TOKEN')
pushover_user = os.getenv('PUSHOVER_USER_KEY')

NEW CODE:
from .settings_bridge import get_pushover_config
pushover_config = get_pushover_config()
pushover_token = pushover_config['token']
pushover_user = pushover_config['user']
"""

# In your queue handler:
"""
OLD CODE:
import os
queue_dir = os.getenv('QUEUE_DIR', './queue')
max_retries = int(os.getenv('MAX_RETRIES', '3'))

NEW CODE:
from .settings_bridge import get_setting
queue_dir = get_setting('QUEUE_DIR', './queue')
max_retries = int(get_setting('MAX_RETRIES', '3'))
"""