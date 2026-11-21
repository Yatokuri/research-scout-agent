import os
import re
from dataclasses import dataclass, field

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.models.groq import GroqModel

from constraint_extractor import extract_constraints
from models import ResearchConstraints, ResearchResult, ResearchPaper
from research_tool import search_papers
from validation import matches_constraints


load_dotenv()

model = GroqModel(os.getenv("LLM_MODEL", "openai/gpt-oss-120b"))


@dataclass
class ResearchState:
    """Store evidence from OpenAlex tool calls during one agent run."""

    constraints: ResearchConstraints

    searches: list[tuple[ResearchConstraints, list[ResearchPaper]]] = field(default_factory=list)


research_agent = Agent(
    model,
    deps_type=ResearchState,
    output_type=str,
    retries=2,
    instructions="""
    You are a research assistant that selects relevant academic papers.

    The user's research constraints have already been extracted.

    You must call search_research_papers exactly once before selecting a paper.

    The tool returns up to 10 OpenAlex candidates.
    Each candidate has a zero-based paper_index.

    Paper abstracts may be shortened to reduce token usage.

    The search tool automatically applies the extracted numerical constraints.
    Do not provide constraints to the tool.

    Select the most relevant candidate for the user's research topic.

    IMPORTANT:
    Return your final answer as plain text, NOT JSON.

    Use exactly this format:

    PAPER_INDEX: 0
    EXPLANATION: Your explanation here.

    Replace 0 with the index of the selected paper.

    If no suitable paper exists, use:

    PAPER_INDEX: NONE
    EXPLANATION: No suitable paper was found.

    Never invent a paper or select an index that was not returned.

    Your explanation must describe:
    1. The paper's main research contribution.
    2. How it relates to the requested research topic.
    3. Why it satisfies the numerical constraints, if any.

    Base research-contribution claims on the paper's abstract.
    Do not invent findings or conclusions unsupported by the retrieved metadata.

    Do not include any additional headings or text outside
    the PAPER_INDEX and EXPLANATION fields.
    """,
)


@research_agent.tool
def search_research_papers(ctx: RunContext[ResearchState],) -> list[dict]:
    """Search OpenAlex and return compact, indexed paper summaries."""

    if ctx.deps.searches:
        _, papers = ctx.deps.searches[0]

    else:
        constraints = ctx.deps.constraints

        papers = search_papers(constraints,max_results=10,)

        ctx.deps.searches.append((constraints, papers))

    return [
        {
            "paper_index": index,
            "title": paper.title,
            "authors": paper.authors[:5],
            "year": paper.year,
            "citation_count": paper.citation_count,
            "citation_source": paper.citation_source,
            "url": paper.url,
            "abstract": paper.abstract[:600],
        }
        for index, paper in enumerate(papers)
    ]


def parse_paper_selection(response: str,) -> tuple[int | None, str]:
    """Extract the selected paper index and explanation from plain text."""

    index_match = re.search(
        r"^PAPER_INDEX:\s*(NONE|\d+)\s*$",
        response,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    explanation_match = re.search(
        r"^EXPLANATION:\s*(.*)",
        response,
        flags=re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )

    if not index_match:
        raise ValueError("The research agent did not return a valid PAPER_INDEX.")

    index_text = index_match.group(1).upper()

    if index_text == "NONE":
        paper_index = None
    else:
        paper_index = int(index_text)

    if explanation_match:
        explanation = explanation_match.group(1).strip()
    else:
        explanation = ""

    if not explanation:
        explanation = "No explanation was provided by the research agent."

    return paper_index, explanation


async def run_research(request: str,) -> tuple[ResearchResult, ResearchConstraints]:
    """Extract constraints, search for papers, and verify the selected result."""

    constraints = await extract_constraints(request)

    state = ResearchState(constraints=constraints)

    result = await research_agent.run(
        request,
        deps=state,
        usage_limits=UsageLimits(
            request_limit=8,
            tool_calls_limit=3,
        ),
    )

    if not state.searches:
        return ResearchResult(
            found=False,
            paper=None,
            explanation="The agent did not search OpenAlex.",
        ), constraints

    _, papers = state.searches[0]

    if not papers:
        return ResearchResult(
            found=False,
            paper=None,
            explanation=(
                "OpenAlex returned no papers satisfying the "
                "specified publication-year and citation constraints "
                "within the retrieved search results."
            ),
        ), constraints

    try:
        paper_index, explanation = parse_paper_selection(
            result.output
        )

    except ValueError as error:
        return ResearchResult(
            found=False,
            paper=None,
            explanation=str(error),
        ), constraints

    if paper_index is None:
        return ResearchResult(
            found=False,
            paper=None,
            explanation=explanation,
        ), constraints

    if not 0 <= paper_index < len(papers):
        return ResearchResult(
            found=False,
            paper=None,
            explanation=(
                f"The agent selected an invalid paper index: "
                f"{paper_index}."
            ),
        ), constraints

    selected_paper = papers[paper_index]

    if not matches_constraints(selected_paper, constraints):
        return ResearchResult(
            found=False,
            paper=None,
            explanation="The selected paper did not satisfy the research constraints.",
        ), constraints

    return ResearchResult(
        found=True,
        paper=selected_paper,
        explanation=explanation,
    ), constraints
