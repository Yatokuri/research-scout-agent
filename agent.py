import os
from dataclasses import dataclass, field

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.models.groq import GroqModel


from constraint_extractor import extract_constraints
from models import ResearchConstraints, ResearchResult, ResearchPaper
from research_tool import search_papers
from verification import verify_result



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
    output_type=ResearchResult,
    retries=2,
    instructions="""
    The user's research constraints have already been extracted.

    You must call search_research_papers before recommending a paper.

    Call search_research_papers exactly once.

    The tool returns up to 10 OpenAlex search results matching the extracted numerical constraints.
    
    Paper abstracts may be shortened to reduce token usage.

    The search tool automatically applies the extracted constraints.
    You do not need to prov ide constraints to the tool.

    Choose the most relevant paper from the returned candidates.

    Never invent paper metadata.
    If no suitable paper is found, return found=False.

    Explain why the selected paper is relevant to the user's topic.

    Your explanation must include:
    1. The paper's main research contribution.
    2. How that contribution relates to the requested topic.
    3. Why it satisfies the numerical constraints, if any.

    Base research-contribution claims on the paper's abstract.
    Do not invent findings or conclusions that are not supported
    by the retrieved metadata.
    """,
)

@research_agent.tool
def search_research_papers(ctx: RunContext[ResearchState],) -> list[dict]:
    """Search OpenAlex and return compact paper summaries."""

    if ctx.deps.searches:
        _, papers = ctx.deps.searches[0]
    else:
        constraints = ctx.deps.constraints

        papers = search_papers(
            constraints,
            max_results=10,
        )

        ctx.deps.searches.append((constraints, papers))

    return [
        {
            "title": paper.title,
            "authors": paper.authors[:5],
            "year": paper.year,
            "citation_count": paper.citation_count,
            "citation_source": paper.citation_source,
            "url": paper.url,
            "abstract": paper.abstract[:600],
        }
        for paper in papers
    ]

async def run_research(request: str) -> tuple[ResearchResult, ResearchConstraints]:
    """Extract constraints, search for papers, and verify the result."""

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

    if all(not papers for _, papers in state.searches):
        return ResearchResult(
            found=False,
            paper=None,
            explanation=(
                "OpenAlex returned no papers satisfying the "
                "specified publication-year and citation constraints "
                "within the retrieved search results."
            ),
        ), constraints

    for search_constraints, papers in state.searches:
        verified = verify_result(
            result.output,
            papers,
            search_constraints,
        )

        if verified.found:
            return verified, constraints

    return ResearchResult(
        found=False,
        paper=None,
        explanation=("No recommendation could be verified against the retrieved OpenAlex results."),
    ), constraints
