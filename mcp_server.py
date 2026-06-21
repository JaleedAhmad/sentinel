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

if __name__ == "__main__":
    mcp.run()
