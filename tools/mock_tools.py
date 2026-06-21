def read_file(path: str) -> dict:
    """Reads the contents of a file at the given path.

    Args:
        path: The file path to read.

    Returns:
        A dict with 'status' and 'content' keys.
    """
    return {"status": "success", "content": f"[mocked file contents for {path}]"}

def send_email(to: str, body: str) -> dict:
    """Sends an email to the given recipient.

    Args:
        to: Recipient email address.
        body: Email body text.

    Returns:
        A dict confirming the send.
    """
    return {"status": "success", "to": to, "confirmation": f"mock-sent body length {len(body)}"}
