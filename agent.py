
import os

from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.models.groq import GroqModel

from dataclasses import dataclass, field

from models import ResearchConstraints, ResearchResult, ResearchPaper
from research_tool import search_papers
from validation import matches_constraints
from verification import verify_result



load_dotenv()

model = GroqModel(os.getenv("LLM_MODEL", "openai/gpt-oss-120b"))


@dataclass
class ResearchState:
    """Store evidence from OpenAlex tool calls during one agent run."""

    searches: list[tuple[ResearchConstraints, list[ResearchPaper]]] = field(default_factory=list)


research_agent = Agent(
    model,
    deps_type=ResearchState,
    output_type=ResearchResult,
    retries=2,
    instructions="""
    You are Research Scout, an AI assistant that finds academic research papers using OpenAlex.

    You must use the search_research_papers tool before recommending any paper.

    Extract the topic, publication-year constraints, and citation-count constraints from the user's request.

    Comparison rules:
    - "before 2021" means year < 2021.
    - "after 2022" means year > 2022.
    - "in 2023" means year == 2023.
    - "at least 100 citations" means >= 100.
    - "more than 100 citations" means > 100.
    - "at most 100 citations" means <= 100.
    - "fewer than 100 citations" means < 100.
    - "approximately 100 citations" means within 10%.

    Select the most relevant paper from the tool results.
    Do not recommend a paper that violates the constraints.

    Never invent titles, authors, years, citation counts, URLs, or abstracts.

    Use only paper metadata returned by the tool.

    If no suitable paper is found, return found=False and explain the limitation.

    Your explanation should describe the paper's contribution and why it matches the user's topic.
    """,
)


@research_agent.tool
def search_research_papers(ctx: RunContext[ResearchState], constraints: ResearchConstraints,) -> list[dict]:
    """Search OpenAlex and store the retrieved evidence."""

    papers = search_papers(constraints, max_results=25)

    ctx.deps.searches.append((constraints, papers))

    return [paper.model_dump() for paper in papers]





async def run_research(request: str) -> ResearchResult:
    """Run the agent and independently verify its selected paper."""

    state = ResearchState()

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
        )

    for constraints, papers in state.searches:
        verified = verify_result(
            result.output,
            papers,
            constraints,
        )

        if verified.found:
            return verified

    return ResearchResult(
        found=False,
        paper=None,
        explanation=(
            "No recommendation could be verified against "
            "the retrieved OpenAlex results."
        ),
    )
