
from typing import Literal

from pydantic import BaseModel, Field, model_validator

class ResearchConstraints(BaseModel):
    """Constraints extracted from the user's research request."""

    topic: str

    year: int | None = None
    year_operator: Literal[ "before", "after", "in", "on_or_before", "on_or_after" ] | None = None

    citation_count: int | None = None
    citation_operator: Literal[ "gt", "gte", "lt", "lte", "approx" ] | None = None


    @model_validator(mode="after")
    def validate_operators(self):
        if (self.year is None) != (self.year_operator is None):
            raise ValueError(
                "Year and year_operator must both be provided or omitted."
            )

        if (self.citation_count is None) != (
            self.citation_operator is None
        ):
            raise ValueError(
                "Citation count and citation_operator must both "
                "be provided or omitted."
            )

        if not self.topic.strip():
            raise ValueError("Research topic cannot be empty.")

        return self



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
