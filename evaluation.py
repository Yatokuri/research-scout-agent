import os

os.environ["PYDANTIC_AI_NO_BANNER"] = "1"

import argparse
import asyncio
import csv
from dataclasses import dataclass
from pathlib import Path

from agent import run_research
from models import ResearchConstraints
from validation import matches_constraints


@dataclass
class EvaluationCase:
    name: str
    prompt: str
    expected: ResearchConstraints
    expected_found: bool | None = None


EVALUATION_CASES = [
    EvaluationCase(
        name="Strict year and citation constraints",
        prompt="Find a research paper about retrieval-augmented generation published before 2021 with more than 500 citations.",
        expected=ResearchConstraints(
            topic="retrieval-augmented generation",
            year=2021,
            year_operator="before",
            citation_count=500,
            citation_operator="gt",
        ),
        expected_found=True,
    ),
    EvaluationCase(
        name="Inclusive citation constraint",
        prompt="Find a machine learning paper published after 2022 with at least 100 citations.",
        expected=ResearchConstraints(
            topic="machine learning",
            year=2022,
            year_operator="after",
            citation_count=100,
            citation_operator="gte",
        ),
        expected_found=True,
    ),
    EvaluationCase(
        name="Exact publication year",
        prompt="Find a paper about transformer architectures published in 2017 with more than 1000 citations.",
        expected=ResearchConstraints(
            topic="transformer architectures",
            year=2017,
            year_operator="in",
            citation_count=1000,
            citation_operator="gt",
        ),
        expected_found=True,
    ),
    EvaluationCase(
        name="Impossible constraints",
        prompt="Find a paper about quantum computing published before 1900 with more than 100000 citations.",
        expected=ResearchConstraints(
            topic="quantum computing",
            year=1900,
            year_operator="before",
            citation_count=100000,
            citation_operator="gt",
        ),
        expected_found=False,
    ),
    EvaluationCase(
        name="No numerical constraints",
        prompt="Find a research paper about reinforcement learning.",
        expected=ResearchConstraints(
            topic="reinforcement learning",
        ),
        expected_found=True,
    ),
    EvaluationCase(
        name="Inclusive year constraint",
        prompt="Find a paper about convolutional neural networks published in 2015 or earlier.",
        expected=ResearchConstraints(
            topic="convolutional neural networks",
            year=2015,
            year_operator="on_or_before",
        ),
    ),
    EvaluationCase(
        name="At most citation constraint",
        prompt="Find a paper about graph neural networks with at most 100 citations.",
        expected=ResearchConstraints(
            topic="graph neural networks",
            citation_count=100,
            citation_operator="lte",
        ),
    ),
    EvaluationCase(
        name="Fewer than citations",
        prompt="Find a paper about federated learning with fewer than 50 citations.",
        expected=ResearchConstraints(
            topic="federated learning",
            citation_count=50,
            citation_operator="lt",
        ),
    ),
    EvaluationCase(
        name="Approximate citations",
        prompt="Find a paper about natural language processing with approximately 500 citations.",
        expected=ResearchConstraints(
            topic="natural language processing",
            citation_count=500,
            citation_operator="approx",
        ),
    ),
    EvaluationCase(
        name="Inclusive recent publication year",
        prompt="Find a paper about large language models published in 2023 or later.",
        expected=ResearchConstraints(
            topic="large language models",
            year=2023,
            year_operator="on_or_after",
        ),
    ),
]


def is_rate_limit_error(error: Exception) -> bool:
    """Check whether an exception represents an HTTP 429 error."""
    return (
        getattr(error, "status_code", None) == 429
        or "status_code: 429" in str(error)
    )


async def run_with_retries(
    prompt: str,
    max_retries: int = 3,
    retry_delay: int = 65,
):
    """Retry requests that fail because of temporary rate limits."""

    for attempt in range(max_retries + 1):
        try:
            result, constraints = await run_research(prompt)
            return result, constraints, attempt

        except Exception as error:
            if not is_rate_limit_error(error) or attempt >= max_retries:
                raise

            print(
                f"Rate limit reached. "
                f"Waiting {retry_delay} seconds before retry "
                f"{attempt + 1}/{max_retries}..."
            )

            await asyncio.sleep(retry_delay)


def save_results(results, output_path: Path):
    """Save evaluation results to a CSV file."""

    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


async def run_evaluation(
    cases: list[EvaluationCase],
    output_path: Path,
    delay: int,
    retry_delay: int,
):
    """Execute evaluation cases and record their results."""

    results = []

    for index, case in enumerate(cases, start=1):
        print(f"\n[{index}/{len(cases)}] {case.name}")
        print(f"Prompt: {case.prompt}")

        row = {
            "test_name": case.name,
            "prompt": case.prompt,
            "constraints_correct": None,
            "expected_constraints": str(case.expected.model_dump()),
            "extracted_constraints": "",
            "expected_found": case.expected_found,
            "found": None,
            "found_correct": None,
            "paper_valid": None,
            "paper_title": "",
            "paper_year": "",
            "paper_citations": "",
            "citation_source": "",
            "paper_url": "",
            "explanation": "",
            "retries": 0,
            "error": "",
        }

        try:
            result, constraints, retries = await run_with_retries(case.prompt, retry_delay=retry_delay)

            expected = case.expected.model_dump()
            extracted = constraints.model_dump()

            constraints_correct = extracted == expected

            paper_valid = (
                matches_constraints(result.paper, case.expected)
                if result.found and result.paper is not None
                else None
            )

            found_correct = (
                result.found == case.expected_found
                if case.expected_found is not None
                else None
            )

            row.update({
                "constraints_correct": constraints_correct,
                "extracted_constraints": str(extracted),
                "found": result.found,
                "found_correct": found_correct,
                "paper_valid": paper_valid,
                "paper_title": result.paper.title if result.paper else "",
                "paper_year": result.paper.year if result.paper else "",
                "paper_citations": result.paper.citation_count if result.paper else "",
                "citation_source": result.paper.citation_source if result.paper else "",
                "paper_url": result.paper.url if result.paper else "",
                "explanation": result.explanation,
                "retries": retries,
            })

            print(f"Constraints correct: {constraints_correct}")
            print(f"Paper found: {result.found}")
            print(f"Paper valid: {paper_valid}")
            print(f"Rate-limit retries: {retries}")

        except Exception as error:
            row["error"] = str(error)
            print(f"Error: {error}")

        results.append(row)

        # Save progress after every case.
        save_results(results, output_path)

        if index < len(cases):
            await asyncio.sleep(delay)

    successful = sum(
        1
        for row in results
        if not row["error"]
        and row["constraints_correct"] is True
        and row["paper_valid"] is not False
        and row["found_correct"] is not False
        and (
            row["found"] is True
            or row["found_correct"] is True
        )
    )

    errors = sum(1 for row in results if row["error"])
    failures = len(results) - successful - errors

    print("\nEvaluation completed.")
    print(f"Successful: {successful}/{len(results)}")
    print(f"Failures: {failures}/{len(results)}")
    print(f"Errors: {errors}/{len(results)}")
    print(f"Results saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate the Research Scout Agent.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--all",
        action="store_true",
        help="Run all evaluation cases.",
    )

    group.add_argument(
        "--case",
        type=int,
        help="Run one evaluation case by its number (1-10).",
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=15,
        help="Seconds to wait between evaluation cases (default: 15).",
    )

    parser.add_argument(
        "--retry-delay",
        type=int,
        default=65,
        help="Seconds to wait after an HTTP 429 error (default: 65).",
    )

    args = parser.parse_args()

    if args.delay < 0 or args.retry_delay < 0:
        parser.error("Delays must be zero or greater.")

    if args.case is not None:
        if not 1 <= args.case <= len(EVALUATION_CASES):
            parser.error(f"Case number must be between 1 and {len(EVALUATION_CASES)}.")

        cases = [EVALUATION_CASES[args.case - 1]]
        output_path = Path(f"evaluation_case_{args.case}.csv")

    else:
        cases = EVALUATION_CASES
        output_path = Path("evaluation_results.csv")

    asyncio.run(run_evaluation(cases, output_path, args.delay, args.retry_delay,)
)


if __name__ == "__main__":
    main()
