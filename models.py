
from typing import Literal

from pydantic import BaseModel, Field

class ResearchConstraints(BaseModel):
    """Constraints extracted from the user's research request."""

    topic: str

    year: int | None = None
    year_operator: Literal[ "before", "after", "in", "on_or_before", "on_or_after" ] | None = None

    citation_count: int | None = None
    citation_operator: Literal[ "gt", "gte", "lt", "lte", "approx" ] | None = None


class ResearchPaper(BaseModel):
    """Metadata about a research paper."""

    title: str
    authors: list[str]
    year: int | None = None
    citation_count: int | None = None
    citation_source: str
    url: str
    abstract: str = ""


class ResearchResult(BaseModel):
    """Structured result returned by the research agent."""

    found: bool = Field(description="Whether a matching paper was found.")

    paper: ResearchPaper | None = None

    explanation: str = Field(description="Why the paper matches the request, or why no match was found.")
