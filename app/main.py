import json
from pathlib import Path
from fastapi import FastAPI, HTTPException, Path as PathParam
from pydantic import BaseModel, Field

# Initialize FastAPI app
app = FastAPI(
    title="Teaching Tools API",
    description="API for accessing curriculum sections for various subjects",
    version="0.1.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Constants
USER_AGENT = "teaching-tools/0.0.1"

# Load data
DATA_PATH = Path("resources/data.json")
with open(DATA_PATH, "r", encoding="utf-8") as f:
    DATA = json.load(f)


class CurriculumSectionResponse(BaseModel):
    """Response model for curriculum section"""

    subject: str = Field(..., description="The subject name")
    section_index: int = Field(..., description="The index of the section")
    content: str = Field(..., description="The curriculum section content")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint providing API information"""
    return {
        "name": "Teaching Tools API",
        "version": "0.1.0",
        "description": "API for accessing curriculum sections",
        "endpoints": {
            "table of contents": "/api/v1/toc",
            "curriculum": "/api/v1/curriculum/{subject}/{section_index}",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    }


@app.get("/api/v1/toc", tags=["Table of Contents"], response_model=dict)
async def get_table_of_contents():
    """Get table of contents for all subjects"""
    toc = {}
    for subject in DATA:
        toc[subject] = DATA[subject]["table_of_contents"]
    return toc


@app.get(
    "/api/v1/curriculum/{subject}/{section_index}",
    tags=["Curriculum"],
    response_model=CurriculumSectionResponse,
    summary="Get curriculum section",
    description="Get a section of the curriculum for a given subject and section index",
)
async def get_curriculum_section(
    subject: str = PathParam(
        ...,
        description="The subject to get the curriculum for (e.g. 'deutsch', 'englisch', 'mathe', 'sachunterricht')",
    ),
    section_index: int = PathParam(
        ...,
        description="The index of the section to get (e.g. 0 for the first section)",
        ge=0,
    ),
):
    """
    Get a section of the curriculum for a given subject and section index.

    - **subject**: The subject name (e.g., "deutsch", "englisch", "mathe", "sachunterricht")
    - **section_index**: The zero-based index of the section to retrieve. Call the /api/v1/toc endpoint to get the section indices for all subjects.
    """
    if subject not in DATA:
        raise HTTPException(
            status_code=404,
            detail=f"Subject '{subject}' not found. Available subjects: {list(DATA.keys())}",
        )

    if "content" not in DATA[subject]:
        raise HTTPException(
            status_code=404, detail=f"Subject '{subject}' does not have content"
        )

    content = DATA[subject]["content"]
    if section_index >= len(content):
        raise HTTPException(
            status_code=404,
            detail=f"Section index {section_index} out of range. Subject '{subject}' has {len(content)} sections (0-{len(content) - 1})",
        )

    return CurriculumSectionResponse(
        subject=subject, section_index=section_index, content=content[section_index]
    )


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
