import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import loader

logger = logging.getLogger(__name__)


def _base_send_email(
    subject: str | None,
    email_html_template: str,
    email_text_template: str,
    from_email: str,
    to_email: str,
):
    """Send a django.core.mail.EmailMultiAlternatives to `to_email`.
    Renders provided templates and send it to to_email
    Low level, Don't use this directly
    """
    # Body
    html_content = loader.render_to_string(email_html_template)
    text_content = loader.render_to_string(email_text_template)
    # Email message
    email_message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,  # Plain text
        from_email=from_email,
        to=[to_email],
    )
    # HTML
    email_message.attach_alternative(html_content, "text/html")
    # Send email
    email_message.send()


def send_email(
    user: User,
    subject: str | None,
    email_html_template: str,
    email_text_template: str,
):
    """Validates email request
    Add common context variable
    """
    _base_send_email(
        subject=subject,
        email_html_template=email_html_template,
        email_text_template=email_text_template,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to_email=user.email,
    )
