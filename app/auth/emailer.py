"""
Pluggable email delivery (spec clause 5): the auth flows are real from
day one, delivery is swappable. The dev transport prints the link to the
server log, so verification/reset can be built, tested, and USED locally
with no email vendor. An SMTP transport is a config swap later.

Security note: the dev transport prints the ACTION LINK (that is its
job); a production transport must never log it.
"""

from __future__ import annotations

from typing import Protocol


class EmailTransport(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


class ConsoleEmailTransport:
    """Development only - prints the mail to stdout/server log."""

    def __init__(self):
        self.outbox: list[tuple[str, str, str]] = []  # kept for tests

    def send(self, to: str, subject: str, body: str) -> None:
        self.outbox.append((to, subject, body))
        print(f"[dev-email] to={to} subject={subject!r}\n{body}\n", flush=True)
