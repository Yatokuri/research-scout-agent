
import pytest

from models import ResearchConstraints, ResearchPaper
from validation import matches_constraints


@pytest.fixture
def sample_paper():
    return ResearchPaper(
        title="Example Research Paper",
        authors=["Example Author"],
        year=2023,
        citation_count=150,
        citation_source="OpenAlex",
        url="https://example.com/paper",
        abstract="An example research paper."
    )


@pytest.mark.parametrize(
    "year,operator,expected",
    [
        (2022, "after", True),
        (2024, "before", True),
        (2023, "in", True),
        (2023, "before", False),
        (2023, "after", False),
        (2022, "on_or_after", True),
        (2023, "on_or_before", True),
    ]
)
def test_year_constraints(sample_paper, year, operator, expected):
    constraints = ResearchConstraints(
        topic="research",
        year=year,
        year_operator=operator
    )

    assert matches_constraints(sample_paper, constraints) == expected


@pytest.mark.parametrize(
    "count,operator,expected",
    [
        (100, "gte", True),
        (150, "gte", True),
        (150, "gt", False),
        (200, "lt", True),
        (150, "lte", True),
        (100, "lte", False),
        (160, "approx", True),
        (200, "approx", False),
    ]
)
def test_citation_constraints(sample_paper, count, operator, expected):
    constraints = ResearchConstraints(
        topic="research",
        citation_count=count,
        citation_operator=operator
    )

    assert matches_constraints(sample_paper, constraints) == expected


def test_combined_constraints(sample_paper):
    constraints = ResearchConstraints(
        topic="research",
        year=2022,
        year_operator="after",
        citation_count=100,
        citation_operator="gte"
    )

    assert matches_constraints(sample_paper, constraints)


def test_reject_invalid_paper(sample_paper):
    constraints = ResearchConstraints(
        topic="research",
        year=2021,
        year_operator="before",
        citation_count=500,
        citation_operator="gt"
    )

    assert not matches_constraints(sample_paper, constraints)
