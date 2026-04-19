"""
Email helper for Tom — read and send emails via Gmail.
"""

import imaplib
import smtplib
import ssl
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from datetime import datetime

EMAIL = "tom.assistent.marian@gmail.com"
APP_PW = "texgzltqekfyzcnw"


def get_unread_emails(sender_filter=None, limit=5):
    """Read unread emails, optionally filter by sender."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PW)
    mail.select("inbox")

    search = "UNSEEN"
    if sender_filter:
        search = f'(UNSEEN FROM "{sender_filter}")'

    _, msgs = mail.search(None, search)
    email_ids = msgs[0].split()[-limit:]  # last N

    results = []
    for eid in email_ids:
        _, data = mail.fetch(eid, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])

        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()

        sender = msg["From"]
        date = msg["Date"]

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")

        results.append({
            "id": eid.decode(),
            "subject": subject,
            "sender": sender,
            "date": date,
            "body": body[:3000],
        })

    mail.logout()
    return results


def send_email(to: str, subject: str, body: str, from_name: str = "Tom (Marians Assistent)"):
    """Send an email."""
    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{EMAIL}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as s:
        s.login(EMAIL, APP_PW)
        s.sendmail(EMAIL, to, msg.as_string())

    return True


if __name__ == "__main__":
    # Test: read latest emails
    emails = get_unread_emails(limit=3)
    for e in emails:
        print(f"Von: {e['sender']}")
        print(f"Betreff: {e['subject']}")
        print(f"Datum: {e['date']}")
        print(f"Inhalt: {e['body'][:200]}...")
        print("---")
