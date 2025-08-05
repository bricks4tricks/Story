import os
import sys
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import auth


def test_send_email_missing_env_vars():
    with patch.object(auth, "SENDER_EMAIL", None), \
         patch.object(auth, "SMTP_SERVER", None), \
         patch.object(auth, "SMTP_PORT", None), \
         patch.object(auth, "SMTP_USERNAME", None), \
         patch.object(auth, "SMTP_PASSWORD", None), \
         patch("smtplib.SMTP") as smtp_mock:
        result = auth.send_email("user@example.com", "Subject", "<p>Hi</p>")
        smtp_mock.assert_not_called()
        assert result is False


def test_send_email_uses_smtp_username_when_sender_missing():
    with patch.object(auth, "SENDER_EMAIL", None), \
         patch.object(auth, "SMTP_SERVER", "smtp.example.com"), \
         patch.object(auth, "SMTP_PORT", 587), \
         patch.object(auth, "SMTP_USERNAME", "user"), \
         patch.object(auth, "SMTP_PASSWORD", "pass"), \
         patch("smtplib.SMTP") as smtp_mock:
        smtp_instance = smtp_mock.return_value.__enter__.return_value
        result = auth.send_email("user@example.com", "Subject", "<p>Hi</p>")
        smtp_mock.assert_called_once_with("smtp.example.com", 587)
        smtp_instance.starttls.assert_called_once()
        smtp_instance.login.assert_called_once_with("user", "pass")
        smtp_instance.send_message.assert_called_once()
        assert result is True
