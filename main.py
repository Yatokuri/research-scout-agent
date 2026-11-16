import asyncio
import os

os.environ["PYDANTIC_AI_NO_BANNER"] = "1"

from agent import run_research


async def main():
    print("Research Scout Agent")
    print("Type 'exit' to quit.\n")

    while True:
        request = input("Research request: ").strip()

        if request.lower() in ("exit", "quit"):
            break

        if not request:
            continue

        try:
            result, constraints = await run_research(request)

            print("\nExtracted constraints:")
            print(constraints.model_dump_json(indent=2))

            if not result.found or result.paper is None:
                print(f"\nNo matching paper found.")
                print(result.explanation)
                continue

            paper = result.paper

            print(f"\nTitle: {paper.title}")
            print(f"Authors: {', '.join(paper.authors)}")
            print(f"Year: {paper.year}")
            print(f"Citations: {paper.citation_count}")
            print(f"Citation source: {paper.citation_source}")
            print(f"URL: {paper.url}")
            print(f"\nExplanation: {result.explanation}\n")

        except Exception as error:
            print(f"\nResearch request failed: {error}\n")


if __name__ == "__main__":
    asyncio.run(main())
