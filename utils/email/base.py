import base64
import logging
import threading
import typing
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

# Reference: https://github.com/django/django/blob/main/django/core/mail/backends/smtp.py


class EmailBackend(BaseEmailBackend, ABC):
    """Generic abstract base for custom email backends."""

    def __init__(self, fail_silently: bool = False, **kwargs: Any) -> None:
        super().__init__(fail_silently=fail_silently, **kwargs)
        self._lock = threading.RLock()  # NOTE: Using Re-entrant lock to ensure thread-safe session usage.

    @typing.override
    def open(self) -> bool | None:
        """Open a network connection."""
        return True

    @typing.override
    def close(self) -> None:
        """Release any resources opened by open(). No-op by default."""

    @typing.override
    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        """Send one or more EmailMessage objects."""
        if not email_messages:
            return 0
        with self._lock:
            new_session_created = self.open()
            if new_session_created is None:
                return 0
            sent_count = 0
            try:
                for message in email_messages:
                    if self._send_message(message):
                        sent_count += 1
            finally:
                if new_session_created:
                    self.close()
        return sent_count

    @abstractmethod
    def _send_message(self, message: EmailMessage) -> bool:
        """Send a single EmailMessage. Return True on success, False on failure."""
        raise NotImplementedError

    @staticmethod
    def _encode_base64(value: bytes | str) -> str:
        if isinstance(value, str):
            value = value.encode("utf-8")
        return base64.b64encode(value).decode("utf-8")


class ApiEmailBackend(EmailBackend):
    """HTTP API-based email backends."""

    def __init__(self, api_endpoint: str | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.email_endpoint = settings.EMAIL_API_URL
        self.timeout = settings.EMAIL_API_TIMEOUT
        self.api_key = getattr(settings, "EMAIL_API_KEY", None)

        if not self.email_endpoint:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires an API endpoint.",
            )

        # NOTE: The current API does not support passing the API key via request headers.
        # Therefore, the API key is appended as a query parameter in the endpoint URL instead.
        self.endpoint = f"{self.email_endpoint}?apiKey={self.api_key}"
        self._session: requests.Session | None = None

    @typing.override
    def open(self) -> bool | None:
        if self._session is not None:
            return False
        try:
            self._session = requests.Session()
            return True
        except requests.RequestException:
            logger.exception("Failed to open email backend session")
            if not self.fail_silently:
                raise
            return None

    @typing.override
    def close(self) -> None:
        if self._session is None:
            return
        try:
            self._session.close()
        finally:
            self._session = None

    @typing.override
    def _send_message(self, message: EmailMessage) -> bool:
        if not message.to:
            logger.warning("Skipping email with no recipients")
            return False

        try:
            if not self._session:
                return False
            response = self._session.post(
                self.endpoint,
                timeout=self.timeout,
                headers=self._build_headers(),
                json=self._build_payload(message),
            )
            if 200 <= response.status_code < 300:
                return self._handle_success(message, response)
            return self._handle_failure(message, response)

        except requests.RequestException:
            logger.exception("Email send failed | subject=%s", message.subject)
            if not self.fail_silently:
                raise
            return False

    def _handle_success(self, message: EmailMessage, response: requests.Response) -> bool:
        logger.info(
            "Email sent | subject=%s | status code=%s",
            message.subject,
            response.status_code,
        )
        return True

    def _handle_failure(self, message: EmailMessage, response: requests.Response) -> bool:
        logger.warning(
            "Email API error | status code=%s | response=%s",
            response.status_code,
            response,
        )
        if not self.fail_silently:
            response.raise_for_status()
        return False

    def _build_headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def _build_payload(self, message: EmailMessage) -> dict[str, Any]:
        recipients_as_string = ",".join(message.to)
        cc_recipients_as_string = ",".join(message.cc)

        return {
            "FromAsBase64": self._encode_base64(settings.DEFAULT_FROM_EMAIL),
            "ToAsBase64": self._encode_base64(recipients_as_string),
            "CcAsBase64": self._encode_base64(cc_recipients_as_string),
            "SubjectAsBase64": self._encode_base64(str(message.subject)),
            "BodyAsBase64": self._encode_base64(str(message.body)),
            "IsBodyHtml": True,
        }
