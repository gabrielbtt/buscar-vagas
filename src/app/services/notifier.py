import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_settings


def build_digest_email(items: list[dict]) -> str:
    lines = ["<h1>Vagas encontradas</h1>", "<ul>"]
    for item in items:
        lines.append(
            f"<li><strong>{item['title']}</strong> - {item['company']} - {item['location']} - score {item['score']:.2f} - <a href='{item['url']}'>abrir vaga</a></li>"
        )
    lines.append("</ul>")
    return "".join(lines)


def send_digest_email(subject: str, html_body: str) -> None:
    settings = get_settings()
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.email_from
    message["To"] = settings.email_to
    message.attach(MIMEText(html_body, "html"))
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(str(settings.email_from), [str(settings.email_to)], message.as_string())
