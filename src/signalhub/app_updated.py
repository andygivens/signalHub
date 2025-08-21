import asyncio
import logging
from aiosmtpd.controller import Controller
from email.message import EmailMessage
from .config import get_smtp_config, load_config
from .handler_updated import handle_email

class SignalHubSMTPHandler:
    """SMTP handler that processes emails using database settings"""
    
    def __init__(self):
        self.config = load_config()
    
    async def handle_DATA(self, server, session, envelope):
        """Handle incoming email data"""
        try:
            # Parse the email message
            message = EmailMessage()
            message.set_content(envelope.content.decode('utf-8', errors='ignore'))
            
            # Add headers
            for key, value in envelope.mail_options.items():
                message[key] = value
            
            # Process the email using current database settings
            handle_email(message, self.config)
            
            return '250 Message accepted for delivery'
        except Exception as e:
            logging.error(f"Error handling email: {e}")
            return '500 Error processing message'

def main():
    """Main entry point for SignalHub SMTP server"""
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting SignalHub SMTP server with database settings...")
    
    # Get SMTP configuration from database
    smtp_config = get_smtp_config()
    
    # Create SMTP handler
    handler = SignalHubSMTPHandler()
    
    # Start SMTP server
    controller = Controller(
        handler, 
        hostname='0.0.0.0', 
        port=2525
    )
    
    try:
        controller.start()
        logging.info(f"SMTP server started on port 2525")
        logging.info(f"Using SMTP relay: {smtp_config.get('host', 'None')}:{smtp_config.get('port', 'None')}")
        
        # Keep running
        import signal
        import sys
        
        def signal_handler(sig, frame):
            logging.info("Shutting down SMTP server...")
            controller.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Wait forever
        signal.pause()
        
    except Exception as e:
        logging.error(f"Failed to start SMTP server: {e}")
        controller.stop()

if __name__ == "__main__":
    main()