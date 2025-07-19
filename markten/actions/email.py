"""
# Markten / Actions / Email

Actions for composing emails
"""

from urllib.parse import urlencode

from markten import ActionSession

from .__misc import open


async def compose(
    action: ActionSession,
    to: str | list[str],
    /,
    cc: str | list[str] | None = None,
    subject: str | None = None,
    body: str | None = None,
) -> None:
    """Compose an email to the given recipient(s)

    This launches a composer in user's preferred mail client, with the given
    information pre-filled.

    Parameters
    ----------
    to : str | list[str]
        Email address(es) to send to.
    cc : str | list[str]
        Email address(es) to send a carbon copy of the email to.
    subject : str
        Email subject.
    body : str
        Email body.

    Implementation based on RFC6086
    https://www.rfc-editor.org/rfc/rfc6068
    """
    if isinstance(to, list):
        to = ",".join(to)

    if isinstance(cc, list):
        cc = ",".join(cc)

    options = urlencode(
        {
            "cc": cc,
            "subject": subject,
            "body": body,
        }
    )

    command = f"mailto:{to}?{options}"

    await open(action, command)
