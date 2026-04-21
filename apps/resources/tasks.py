import logging

from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string

from apps.resources.models import ContactRequest, RequestDemo
from apps.resources.utils import get_contact_request_email_context, get_demo_request_email_context
from utils.email.service import send_email

logger = logging.getLogger(__name__)


@shared_task
def send_contact_request_email(contact_id: int):
    instance = ContactRequest.objects.filter(id=contact_id).first()
    if not instance:
        return None

    recipient = settings.EMAIL_TO
    email_subject = "You got a new feedback!"
    email_context = get_contact_request_email_context(instance)
    html_body = render_to_string("email/contact_request.html", email_context)

    send_email(
        subject=email_subject,
        to_email=[recipient],
        html=html_body,
    )
    return True


@shared_task
def send_demo_request_email(request_demo_id: int):
    instance = RequestDemo.objects.select_related("tool").prefetch_related("tool__owners").filter(id=request_demo_id).first()
    if not instance:
        return None

    tool_owners = instance.tool.owners.all()

    if not tool_owners.exists():
        logger.info("skipping cause there are no tool owners associated with this tool")
        return False

    recipients = list(tool_owners.values_list("email", flat=True))
    email_subject = "You got a new request for demo!"
    email_context = get_demo_request_email_context(instance)
    html = render_to_string("email/request_demo.html", email_context)
    send_email(
        subject=email_subject,
        to_email=recipients,
        html=html,
        cc_email=[settings.EMAIL_TO],
    )
    return True
