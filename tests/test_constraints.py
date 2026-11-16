
import pytest
from pydantic import ValidationError

from models import ResearchConstraints


def test_valid_constraints():
    constraints = ResearchConstraints(
        topic="machine learning",
        year=2021,
        year_operator="before",
        citation_count=500,
        citation_operator="gt",
    )

    assert constraints.year == 2021
    assert constraints.citation_operator == "gt"


def test_reject_year_without_operator():
    with pytest.raises(ValidationError):
        ResearchConstraints(
            topic="machine learning",
            year=2021,
        )


def test_reject_operator_without_year():
    with pytest.raises(ValidationError):
        ResearchConstraints(
            topic="machine learning",
            year_operator="before",
        )


def test_reject_citations_without_operator():
    with pytest.raises(ValidationError):
        ResearchConstraints(
            topic="machine learning",
            citation_count=500,
        )


def test_reject_empty_topic():
    with pytest.raises(ValidationError):
        ResearchConstraints(topic="   ")
