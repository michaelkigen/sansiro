from smtplib import SMTPException
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Verifications
import string
import random
from django.core.mail import EmailMultiAlternatives
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def orderdfood_emailer(user_details, ordered_food, order_id):
    subject = 'Food Order'
    from_email = 'brianwgatundu@gmail.com'
    to_email = 'michaelmaiyo44@gmail.com'

    # Render the HTML content from the template
    html_message = render_to_string('email_template.html', {'user_details': user_details, 'ordered_food': ordered_food, 'order_id': order_id})

    # Create the plain text version of the email
    plain_message = strip_tags(html_message)

    # Create the email message
    email_message = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
    email_message.attach_alternative(html_message, 'text/html')

    try:
        email_message.send()
        # Email sent successfully
        return 'Email sent successfully.'
    except Exception as e:
        # Handle the exception
        print(f"Email sending failed: {e}")
        # Provide an error message to the user
        return 'Failed to send the email. Please try again later.'



def generate_verification_code(length=4):
    characters = string.digits  # You can customize the characters used in the verification code
    verification_code = ''.join(random.choice(characters) for _ in range(length))
    return verification_code




def send_center_sms(data, user):
    try:
        print('step 1')
        account_sid = "AC94d634c48c7f12dfb8f6af8f0b1614c2"
        auth_token = "50917f3e65a520aeb570f376e9b1a5e5"
        client = Client(account_sid, auth_token)

        # Format the data and user details for better readability
        formatted_data = '\n'.join([f"{item['food_name']}: {item['quantity']} x {item['sub_total']}" for item in data])
        formatted_user = f"User ID: {user['user_id']}\nPhone: {user['user_phone_number']}\nName: {user['user_first_name']} {user['user_last_name']}"

        # Construct the final message
        message_body = f"New order:\n{formatted_data}\n\n{formatted_user}"

        message = client.messages.create(
            body=message_body,
            from_='+13343842451',
            to='+254797759614'
        )
        print('step 3')
    except TwilioRestException as e:
        print(f"Twilio error: {e}")
        # Handle the exception or return an error response
        return f'Failed {e}'




