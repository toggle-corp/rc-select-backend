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


class EmailBackend(BaseEmailBackend, ABC):
    """Abstract Django email backend for sending emails via an HTTP API."""

    def __init__(
        self,
        api_endpoint: str | None = None,
        timeout: int | None = None,
        fail_silently: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(fail_silently=fail_silently, **kwargs)

        self.endpoint: str = api_endpoint or getattr(settings, "EMAIL_API_ENDPOINT", "")
        self.timeout: int = timeout if timeout is not None else getattr(settings, "EMAIL_API_TIMEOUT", 10)

        if not self.endpoint:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} requires an API endpoint.",
            )

        self._session: requests.Session | None = None
        self._lock = threading.RLock()

    @typing.override
    def open(self) -> bool | None:
        """Open a requests.Session if one is not already open."""
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
        """Close and discard the current session."""
        if self._session is None:
            return
        try:
            self._session.close()
        finally:
            self._session = None

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

    def _send_message(self, message: EmailMessage) -> bool:
        """Send a single EmailMessage via the API."""
        if not message.to:
            logger.warning("Skipping email with no recipients")
            return False

        try:
            payload = self._build_payload(message)
            response = self._session.post(
                self.endpoint,
                json=payload,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return self._handle_success(message, response)
            return self._handle_failure(message, response)

        except requests.RequestException:
            logger.exception(
                "Email send failed | subject=%s | to=%s",
                message.subject,
                ", ".join(message.to),
            )
            if not self.fail_silently:
                raise
            return False

    def _handle_success(self, message: EmailMessage, response: requests.Response) -> bool:
        """Called when the API returns HTTP 200."""
        logger.info(
            "Email sent | subject=%s | to=%s | response=%s",
            message.subject,
            ", ".join(message.to),
            response.text,
        )
        return True

    def _handle_failure(self, message: EmailMessage, response: requests.Response) -> bool:
        """Called when the API returns a non-200 status."""
        logger.warning(
            "Email API error | status=%s | subject=%s | to=%s | response=%s",
            response.status_code,
            message.subject,
            ", ".join(message.to),
            response.text,
        )
        if not self.fail_silently:
            response.raise_for_status()
        return False

    @abstractmethod
    def _build_payload(self, message: EmailMessage) -> dict[str, Any]:
        """Convert a Django EmailMessage into the provider's JSON payload."""
        ...

    @staticmethod
    def _encode_base64(value: bytes | str) -> str:
        """Base64-encode bytes or a UTF-8 string."""
        if isinstance(value, str):
            value = value.encode("utf-8")
        return base64.b64encode(value).decode("utf-8")
