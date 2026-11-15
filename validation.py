
from models import ResearchConstraints, ResearchPaper


def matches_constraints(paper: ResearchPaper, constraints: ResearchConstraints) -> bool:
    """Check whether a paper satisfies the numerical constraints."""

    if constraints.year is not None:
        if paper.year is None or constraints.year_operator is None:
            return False

        year = paper.year
        target = constraints.year

        if constraints.year_operator == "before" and not year < target:
            return False

        if constraints.year_operator == "after" and not year > target:
            return False

        if constraints.year_operator == "in" and year != target:
            return False

        if constraints.year_operator == "on_or_before" and not year <= target:
            return False

        if constraints.year_operator == "on_or_after" and not year >= target:
            return False

    if constraints.citation_count is not None:
        if (paper.citation_count is None or constraints.citation_operator is None):
            return False

        citations = paper.citation_count
        target = constraints.citation_count

        if constraints.citation_operator == "gt" and not citations > target:
            return False

        if constraints.citation_operator == "gte" and not citations >= target:
            return False

        if constraints.citation_operator == "lt" and not citations < target:
            return False

        if constraints.citation_operator == "lte" and not citations <= target:
            return False

        if constraints.citation_operator == "approx":
            tolerance = max(1, target * 0.1)

            if abs(citations - target) > tolerance:
                return False

    return True


def filter_papers(papers: list[ResearchPaper], constraints: ResearchConstraints) -> list[ResearchPaper]:
    """Return only papers satisfying the numerical constraints."""

    return [paper for paper in papers if matches_constraints(paper, constraints)]
