import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from app.config import Settings, get_settings

logger = logging.getLogger("mealmate.mailer")


@dataclass
class MailPayload:
    to_email: str
    subject: str
    body: str
    outbox_file: str | None = None


class BaseMailer:
    def send(self, payload: MailPayload) -> None:
        raise NotImplementedError


class OutboxMailer(BaseMailer):
    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, payload: MailPayload) -> None:
        outbox_file = Path(payload.outbox_file or self.settings.mail_outbox_path)
        outbox_file.parent.mkdir(parents=True, exist_ok=True)
        with outbox_file.open("a", encoding="utf-8") as handle:
            handle.write(f"TO: {payload.to_email}\n")
            handle.write(f"SUBJECT: {payload.subject}\n")
            handle.write(f"BODY: {payload.body}\n")
            handle.write("---\n")
        logger.info("mail_written_to_outbox to=%s path=%s", payload.to_email, outbox_file)


class SMTPMailer(BaseMailer):
    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, payload: MailPayload) -> None:
        if not self.settings.smtp_host:
            raise RuntimeError("SMTP host is not configured")
        msg = EmailMessage()
        msg["From"] = self.settings.smtp_from
        msg["To"] = payload.to_email
        msg["Subject"] = payload.subject
        msg.set_content(payload.body)
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as server:
            server.starttls()
            if self.settings.smtp_user and self.settings.smtp_password:
                server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.send_message(msg)
        logger.info("mail_sent_via_smtp to=%s", payload.to_email)


def get_mailer(settings: Settings | None = None) -> BaseMailer:
    resolved = settings or get_settings()
    if resolved.prod_mode:
        return SMTPMailer(resolved)
    return OutboxMailer(resolved)
