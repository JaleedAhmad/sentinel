import sys
from fastmcp import FastMCP

mcp = FastMCP("sentinel-target-tools")

@mcp.tool
def read_file(path: str) -> dict:
    """Reads the contents of a file at the given path.
    Args:
        path: The file path to read.
    """
    print(f"[MCP SERVER] read_file called with path: {path}", file=sys.stderr)
    return {"status": "success", "content": f"[mocked file contents for {path}]"}

@mcp.tool
def send_email(to: str, body: str) -> dict:
    """Sends an email to the given recipient.
    Args:
        to: Recipient email address.
        body: Email body text.
    """
    print(f"[MCP SERVER] send_email called to: {to}", file=sys.stderr)
    return {"status": "success", "to": to, "confirmation": f"mock-sent body length {len(body)}"}

@mcp.tool
def delete_file(path: str) -> dict:
    """Deletes a file at the given path.
    Args:
        path: The file path to delete.
    """
    print(f"[MCP SERVER] delete_file called with path: {path}", file=sys.stderr)
    return {"status": "success", "deleted": path, "confirmation": "mock-deleted"}

@mcp.tool
def transfer_funds(account: str, amount: float) -> dict:
    """Transfers funds to a specified account.
    Args:
        account: Destination account identifier.
        amount: Amount to transfer.
    """
    print(f"[MCP SERVER] transfer_funds called to account: {account} amount: {amount}", file=sys.stderr)
    return {"status": "success", "account": account, "amount": amount, "confirmation": "mock-transferred"}

if __name__ == "__main__":
    mcp.run()
