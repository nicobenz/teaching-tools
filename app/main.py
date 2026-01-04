import json
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP(name="teaching-tools", json_response=False, stateless_http=False)

# Constants
USER_AGENT = "teaching-tools/1.0"

with open("resources/data.json", "r") as f:
    DATA = json.load(f)


@mcp.tool()
async def get_curriculum_section(subject: str, section_index: int) -> str:
    """Get a section of the curriculum for a given subject and section index.

    Args:
        subject: The subject to get the curriculum for (e.g. "deutsch", "englisch", "mathe", "sachunterricht")
        section_index: The index of the section to get (e.g. 0 for the first section)
    """

    return DATA[subject]["content"][section_index]


def main():
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
