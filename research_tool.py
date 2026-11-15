
import os

import httpx
from dotenv import load_dotenv

from models import ResearchConstraints, ResearchPaper
from validation import filter_papers


load_dotenv()

OPENALEX_API_URL = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index: dict | None) -> str:
    """Convert an OpenAlex inverted index into readable text."""
    if not inverted_index:
        return ""

    words = {}

    for word, positions in inverted_index.items():
        for position in positions:
            words[position] = word

    return " ".join(words[position] for position in sorted(words))


def build_openalex_filters(constraints: ResearchConstraints) -> str:
    """Convert publication-year constraints into OpenAlex filters."""

    if constraints.year is None:
        return ""

    year = constraints.year
    operator = constraints.year_operator

    if operator == "before":
        return f"publication_year:<{year}"

    if operator == "after":
        return f"publication_year:>{year}"

    if operator == "in":
        return f"publication_year:{year}"

    if operator == "on_or_before":
        return f"publication_year:<{year + 1}"

    if operator == "on_or_after":
        return f"publication_year:>{year - 1}"

    return ""


def remove_duplicates(papers: list[ResearchPaper]) -> list[ResearchPaper]:
    """Remove duplicate papers based on title and publication year."""

    unique_papers = {}

    for paper in papers:
        key = (
            " ".join(paper.title.lower().split()),
            paper.year
        )

        existing = unique_papers.get(key)

        if (
            existing is None
            or (paper.citation_count or 0) > (existing.citation_count or 0)
        ):
            unique_papers[key] = paper

    return list(unique_papers.values())


def search_papers(
    constraints: ResearchConstraints,
    max_results: int = 10
) -> list[ResearchPaper]:
    """Search OpenAlex and return papers matching numerical constraints."""

    params = {
        "search": constraints.topic,
        "per_page": max(1, min(max_results, 100)),
    }

    filters = build_openalex_filters(constraints)

    if filters:
        params["filter"] = filters

    api_key = os.getenv("OPENALEX_API_KEY")

    if api_key:
        params["api_key"] = api_key

    with httpx.Client(timeout=20.0) as client:
        response = client.get(OPENALEX_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

    papers = []

    for work in data.get("results", []):
        authors = [
            authorship["author"]["display_name"]
            for authorship in work.get("authorships", [])
            if authorship.get("author")
            and authorship["author"].get("display_name")
        ]

        title = work.get("title")
        url = work.get("doi") or work.get("id")

        if not title or not url:
            continue

        paper = ResearchPaper(
            title=title,
            authors=authors,
            year=work.get("publication_year"),
            citation_count=work.get("cited_by_count"),
            citation_source="OpenAlex",
            url=url,
            abstract=reconstruct_abstract(
                work.get("abstract_inverted_index")
            ),
        )

        papers.append(paper)

    unique_papers = remove_duplicates(papers)

    return filter_papers(unique_papers, constraints)


if __name__ == "__main__":
    constraints = ResearchConstraints(
        topic="retrieval augmented generation",
        year=2021,
        year_operator="before",
        citation_count=500,
        citation_operator="gt",
    )

    results = search_papers(constraints, max_results=25)

    if not results:
        print("No matching papers found in the retrieved results.")

    for paper in results:
        print(f"Title: {paper.title}")
        print(f"Authors: {', '.join(paper.authors)}")
        print(f"Year: {paper.year}")
        print(f"Citations: {paper.citation_count}")
        print(f"Source: {paper.citation_source}")
        print(f"URL: {paper.url}")
        print("-" * 50)
