from pydantic import BaseModel


class ServerConfig(BaseModel):
    """Server Confgiguration."""

    host: str
    port: int
    transport: str
    url: str


def get_mcp_server_config() -> ServerConfig:
    """Get the MCP server configuration."""
    return ServerConfig(
        host="localhost",
        port=10100,
        transport="sse",
        url="http://localhost:10100/sse",
    )
