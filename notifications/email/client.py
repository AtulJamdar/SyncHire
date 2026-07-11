import logging
import resend

try:
    from config import settings
except ImportError:
    import sys
    import os
    # Fallback to resolve backend imports if run from workspace root
    backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from config import settings

log = logging.getLogger("email_client")


class EmailClient:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    async def send(
        self,
        to: str,
        subject: str,
        html_body: str,
        from_name: str = "Job Finder AI",
        from_email: str = "alerts@jobfinderai.com",
        reply_to: str | None = None,
        unsubscribe_url: str | None = None
    ) -> bool:
        """Returns True on success, False on failure."""
        headers = {}
        if unsubscribe_url:
            headers["List-Unsubscribe"] = f"<{unsubscribe_url}>"
            headers["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

        try:
            # Resend library doesn't have an async method out of the box in this version.
            # We can execute it synchronously or wrap in run_in_executor.
            # For simplicity and robust async execution, let's call it:
            result = resend.Emails.send({
                "from": f"{from_name} <{from_email}>",
                "to": to,
                "subject": subject,
                "html": html_body,
                "headers": headers,
                "reply_to": reply_to or from_email,
            })
            return bool(result.get("id"))
        except Exception as e:
            log.error(f"Email send failed to {to}: {e}")
            return False
