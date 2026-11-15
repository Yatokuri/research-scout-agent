
from models import ResearchConstraints, ResearchPaper, ResearchResult
from verification import verify_result


def make_paper(
    title="Example Paper",
    year=2020,
    citations=600,
):
    return ResearchPaper(
        title=title,
        authors=["Example Author"],
        year=year,
        citation_count=citations,
        citation_source="OpenAlex",
        url="https://openalex.org/W123",
        abstract="Example abstract.",
    )


def make_constraints():
    return ResearchConstraints(
        topic="machine learning",
        year=2021,
        year_operator="before",
        citation_count=500,
        citation_operator="gt",
    )


def test_accept_valid_paper():
    paper = make_paper()

    result = ResearchResult(
        found=True,
        paper=paper,
        explanation="Relevant to the topic.",
    )

    verified = verify_result(
        result,
        [paper],
        make_constraints(),
    )

    assert verified.found is True
    assert verified.paper == paper


def test_reject_fabricated_paper():
    real_paper = make_paper()
    fabricated = make_paper(title="Invented Research Paper")

    result = ResearchResult(
        found=True,
        paper=fabricated,
        explanation="Relevant to the topic.",
    )

    verified = verify_result(
        result,
        [real_paper],
        make_constraints(),
    )

    assert verified.found is False
    assert verified.paper is None


def test_restore_original_metadata():
    real_paper = make_paper(citations=600)
    modified = make_paper(citations=999999)

    result = ResearchResult(
        found=True,
        paper=modified,
        explanation="Relevant to the topic.",
    )

    verified = verify_result(
        result,
        [real_paper],
        make_constraints(),
    )

    assert verified.found is True
    assert verified.paper.citation_count == 600


def test_reject_constraint_violation():
    paper = make_paper(year=2023)

    result = ResearchResult(
        found=True,
        paper=paper,
        explanation="Relevant to the topic.",
    )

    verified = verify_result(
        result,
        [paper],
        make_constraints(),
    )

    assert verified.found is False
    assert verified.paper is None


def test_handle_no_result():
    result = ResearchResult(
        found=False,
        paper=None,
        explanation="No matching paper found.",
    )

    verified = verify_result(
        result,
        [],
        make_constraints(),
    )

    assert verified.found is False
    assert verified.paper is None
