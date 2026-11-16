
import os

from dotenv import load_dotenv
from pydantic_ai import Agent, UsageLimits
from pydantic_ai.models.groq import GroqModel

from models import ResearchConstraints


load_dotenv()

model = GroqModel(
    os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
)

constraint_agent = Agent(
    model,
    output_type=ResearchConstraints,
    retries=2,
    instructions="""
    Extract research constraints from the user's request.

    Return only the structured ResearchConstraints fields.

    The topic must describe the research subject.

    Year operators:
    - "before 2021" -> before, 2021
    - "after 2022" -> after, 2022
    - "in 2023" -> in, 2023
    - "2021 or earlier" -> on_or_before, 2021
    - "2021 or later" -> on_or_after, 2021

    Citation operators:
    - "more than 500" -> gt, 500
    - "at least 500" -> gte, 500
    - "fewer than 500" -> lt, 500
    - "at most 500" -> lte, 500
    - "approximately 500" -> approx, 500

    If a constraint is not mentioned, use null for both
    its numerical value and operator.

    Never invent numerical constraints.

    If a request is ambiguous, do not guess its meaning.
    Do not reinterpret strict comparisons as inclusive ones.
    """,
)


async def extract_constraints(request: str) -> ResearchConstraints:
    """Extract structured constraints from natural language."""

    result = await constraint_agent.run(
        request,
        usage_limits=UsageLimits(request_limit=5),
    )

    return result.output
