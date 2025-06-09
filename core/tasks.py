import logging
import smtplib
import imaplib
import email
import uuid
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.utils import timezone
from celery import shared_task
from .models import EmailConfiguration, EmailCheck

logger = logging.getLogger('core')


@shared_task
def send_test_email(config_id):
    """Send a test email using the specified configuration"""
    try:
        config = EmailConfiguration.objects.get(id=config_id, is_active=True)
    except EmailConfiguration.DoesNotExist:
        logger.error(f"Configuration with ID {config_id} not found or inactive")
        return False

    # Generate a unique message ID
    timestamp = int(time.time())
    message_id = f"ping-test-{timestamp}-{uuid.uuid4().hex[:8]}"
    subject = f"Email Check: {message_id}"

    # Create the email check record
    email_check = EmailCheck.objects.create(
        configuration=config,
        message_id=message_id,
        subject=subject,
        status='pending'
    )

    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = config.sender_email
        msg['To'] = config.receiver_email
        msg['Subject'] = subject

        # Add a unique identifier in the body and headers
        body = f"""
        This is an automated test email from the Email Checker system.

        Message ID: {message_id}
        Sent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

        This email is used to verify email delivery between {config.sender_email} and {config.receiver_email}.
        """
        msg.attach(MIMEText(body, 'plain'))
        msg.add_header('X-Email-Checker-ID', message_id)

        # Connect to SMTP server and send the email
        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.sender_email, config.sender_password)
            server.send_message(msg)

        # Update the email check record
        sent_time = timezone.now()
        email_check.sent_at = sent_time
        email_check.status = 'sent'
        email_check.save()

        logger.info(f"Test email sent successfully: {message_id}")

        # Schedule a task to check for the email
        check_for_email.apply_async(
            args=[config_id, message_id, email_check.id],
            countdown=60  # Wait 1 minute before checking
        )

        return True

    except Exception as e:
        # Update the email check record with the error
        email_check.status = 'failed'
        email_check.error_message = str(e)
        email_check.save()

        logger.error(f"Failed to send test email: {str(e)}")
        return False


@shared_task
def check_for_email(config_id, message_id, check_id, max_retries=5, retry_count=0):
    """Check if the test email has been received"""
    try:
        config = EmailConfiguration.objects.get(id=config_id, is_active=True)
        email_check = EmailCheck.objects.get(id=check_id)
    except (EmailConfiguration.DoesNotExist, EmailCheck.DoesNotExist):
        logger.error(f"Configuration or email check not found: {config_id}, {check_id}")
        return False

    try:
        # Connect to IMAP server
        mail = imaplib.IMAP4_SSL(config.imap_server, config.imap_port)
        mail.login(config.receiver_email, config.receiver_password)
        mail.select('inbox')

        # Search for emails with the specific message ID
        search_criteria = f'(HEADER X-Email-Checker-ID "{message_id}")'
        result, data = mail.search(None, search_criteria)

        if result == 'OK' and data[0]:
            # Email found
            email_ids = data[0].split()
            for email_id in email_ids:
                result, msg_data = mail.fetch(email_id, '(RFC822)')
                raw_email = msg_data[0][1]

                # Parse the email
                msg = email.message_from_bytes(raw_email)

                # Verify it's our test email
                if msg['X-Email-Checker-ID'] == message_id:
                    # Update the email check record
                    received_time = timezone.now()
                    email_check.received_at = received_time
                    email_check.status = 'received'

                    # Calculate delivery time
                    if email_check.sent_at:
                        email_check.delivery_time = received_time - email_check.sent_at

                    email_check.save()

                    logger.info(f"Test email received successfully: {message_id}")
                    mail.logout()
                    return True

            # If we get here, we didn't find the exact email
            mail.logout()

        # Email not found yet
        if retry_count < max_retries:
            # Schedule another check
            logger.info(f"Email not found yet, scheduling retry {retry_count + 1}/{max_retries}: {message_id}")
            check_for_email.apply_async(
                args=[config_id, message_id, check_id, max_retries, retry_count + 1],
                countdown=60  # Wait 1 minute before retrying
            )
            return None
        else:
            # Max retries reached, mark as failed
            email_check.status = 'failed'
            email_check.error_message = "Email not received after maximum retries"
            email_check.save()

            logger.warning(f"Email not received after {max_retries} retries: {message_id}")
            mail.logout()
            return False

    except Exception as e:
        # If this is not the last retry, schedule another check
        if retry_count < max_retries:
            logger.warning(f"Error checking for email, will retry: {str(e)}")
            check_for_email.apply_async(
                args=[config_id, message_id, check_id, max_retries, retry_count + 1],
                countdown=60  # Wait 1 minute before retrying
            )
            return None
        else:
            # Max retries reached, mark as failed
            email_check.status = 'failed'
            email_check.error_message = f"Error checking for email: {str(e)}"
            email_check.save()

            logger.error(f"Failed to check for email: {str(e)}")
            return False


@shared_task
def schedule_email_checks():
    """Schedule email checks for all active configurations"""
    configs = EmailConfiguration.objects.filter(is_active=True)
    for config in configs:
        # Check if we need to run a check for this configuration
        last_check = EmailCheck.objects.filter(configuration=config).order_by('-created_at').first()

        should_run = False
        if not last_check:
            # No previous checks, run one now
            should_run = True
        else:
            # Check if it's time for a new check based on the interval
            time_since_last = timezone.now() - last_check.created_at
            if time_since_last > timedelta(minutes=config.check_interval):
                should_run = True

        if should_run:
            logger.info(f"Scheduling email check for configuration: {config.name}")
            send_test_email.delay(config.id)
