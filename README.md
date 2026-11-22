# Research Scout Agent

Research Scout Agent is a Python-based AI application that helps users discover academic research papers through natural-language requests.

The application uses PydanticAI and a Groq-hosted language model to understand research requests and identify relevant papers using the OpenAlex API.

Users can search for papers based on a research topic, publication year, and citation count.

## Features

- Search for academic research papers using natural language.
- Extract publication-year and citation-count constraints.
- Retrieve real research papers and metadata from OpenAlex.
- Filter papers based on numerical constraints.
- Recommend a relevant paper and explain why it matches the request.
- Verify selected papers against retrieved OpenAlex data.
- Return a clear message when no suitable paper is found.

## Technologies

- **Python** — Application logic.
- **PydanticAI** — AI agents and tool integration.
- **Groq** — Hosts the language model.
- **OpenAlex API** — Provides academic research metadata.
- **Pydantic** — Structured data models and validation.
- **HTTPX** — HTTP requests to OpenAlex.
- **python-dotenv** — Environment variable configuration.
- **pytest** — Automated testing.

## LLM Selection

The project uses the `openai/gpt-oss-120b` model through the Groq API.

Groq was selected because it provides API access to capable language models through a free tier, making it suitable for developing and testing a student project without requiring a paid subscription.

The selected model supports tool calling and can be integrated with PydanticAI using `GroqModel`. These capabilities are important because the research agent must retrieve external information rather than relying solely on the language model's internal knowledge.

The model is used for two main tasks:

- **Constraint Extraction:** Interpreting natural-language research requests and extracting structured search constraints.
- **Paper Selection:** Evaluating retrieved candidates, selecting a relevant paper, and generating an explanation.

Publication-year and citation-count validation are handled by deterministic Python code rather than relying on the language model.

### API Limitations

During development, the Groq free tier for `openai/gpt-oss-120b` had the following documented limits:

- 30 requests per minute.
- 1,000 requests per day.
- 8,000 tokens per minute.
- 200,000 tokens per day.

These limits can change and may depend on the account's usage tier.

The project encountered rate-limit errors during repeated evaluation runs. To reduce these errors, the evaluation script supports delays between requests and retries when HTTP 429 responses occur.

The research agent initially used structured Pydantic output, but some responses caused parsing errors. The final implementation uses a simpler plain-text format for paper selection, while retaining Pydantic models for extracted constraints and final research results.

## Prerequisites

Before running the application, make sure you have:

- Python 3.14 or a compatible version.
- Git (for cloning the repository).
- A Groq API key.
- An OpenAlex API key.

API keys can be obtained from:

- [Groq Console](https://console.groq.com/)
- [OpenAlex](https://openalex.org/)

### Obtaining API Keys

The application requires API keys for Groq and OpenAlex.

**Groq API Key:**
1. Visit [Groq Console](https://console.groq.com/).
2. Create an account or sign in.
3. Navigate to **API Keys** and generate a new API key.
4. Copy the key into the `GROQ_API_KEY` variable in your `.env` file.

**OpenAlex API Key:**
1. Visit [OpenAlex](https://openalex.org/).
2. Register or sign in.
3. Follow the API key registration instructions to obtain your key.
4. Copy the key into the `OPENALEX_API_KEY` variable in your `.env` file.

Keep your API keys private. The `.env` file should not be committed to GitHub.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Yatokuri/research-scout-agent.git
cd research-scout-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root.

You can copy `.env.example` and fill in your API keys.

```dotenv
GROQ_API_KEY=your_groq_api_key
OPENALEX_API_KEY=your_openalex_api_key
LLM_MODEL=openai/gpt-oss-120b
```

The application uses the Groq-hosted `openai/gpt-oss-120b` model by default.

## Running the Application

Start the command-line interface:

```bash
python main.py
```

The application will prompt you to enter a research request.

Example:

```text
Research Scout Agent
Type 'exit' to quit.

Research request: Find a research paper about retrieval-augmented generation published before 2021 with more than 500 citations.
```

The application displays:

- Extracted research constraints.
- Paper title and authors.
- Publication year.
- Citation count and citation source.
- DOI or OpenAlex URL.
- An explanation of why the paper matches the request.

Enter `exit` or `quit` to close the application.

## Agent Workflow

The Research Scout Agent uses two PydanticAI agents and a custom OpenAlex search tool to process research requests.

The workflow consists of six steps:

1. **User Request:** The user enters a natural-language request describing a research topic and optional publication-year or citation-count constraints.

2. **Constraint Extraction (LLM):** The constraint extraction agent converts the request into a structured `ResearchConstraints` model using PydanticAI and Pydantic. It identifies the research topic, numerical values, and comparison operators.

3. **Paper Search (Custom Tool):** The research agent calls `search_research_papers`, which uses the OpenAlex API to retrieve matching academic publications. Search filters are applied based on the extracted constraints.

4. **Constraint Filtering (Python):** Duplicate results are removed, and retrieved papers are checked against publication-year and citation-count requirements using deterministic Python validation.

5. **Paper Selection (LLM):** The research agent receives up to 10 matching candidates and selects the most relevant paper by its index. It also generates an explanation based on the retrieved metadata and abstract.

6. **Final Validation (Python):** The selected index is checked against the retrieved candidates, and the paper's numerical constraints are validated again. The application returns the original OpenAlex metadata rather than allowing the language model to generate paper details.

If no matching papers are retrieved, or the selected result fails validation, the application returns a no-result response.

This approach separates language-model reasoning from deterministic validation, reducing the risk of fabricated paper metadata and incorrect numerical comparisons.

## Running Tests

The project includes automated tests for constraint validation and result verification.

Run all tests using:

```bash
python -m pytest -v
```

These tests check that publication-year and citation-count constraints are handled correctly and that unverified papers are rejected.

## Main Components

**`main.py`**

Provides the command-line interface and displays research results.

**`constraint_extractor.py`**

Uses a language model to extract structured research constraints from natural-language requests.

**`agent.py`**

Defines the PydanticAI research agent, integrates the OpenAlex search tool, and validates selected papers against the retrieved candidates and numerical constraints.

**`models.py`**

Defines the structured Pydantic models used throughout the application.

**`research_tool.py`**

Queries OpenAlex, retrieves research metadata, and applies API filters.

**`validation.py`**

Checks publication-year and citation-count constraints using deterministic Python logic.

**`verification.py`**

Contains additional paper-verification utilities and tests for checking recommendations against retrieved OpenAlex data.

**`evaluation.py`**

Runs the evaluation cases, compares extracted constraints against expected values, validates returned papers and source metadata, and exports evaluation results to CSV.

**`tests/`**

Contains automated pytest tests for constraint handling, numerical validation, and paper-verification utilities.

## Evaluation

The evaluation automatically checks constraint extraction and numerical validity. Paper relevance and explanation accuracy were reviewed qualitatively rather than measured using an automated scoring system.

### Evaluation Methodology

The evaluation approach was informed by the Pydantic Evals documentation, which describes evaluating AI applications using predefined test cases, deterministic checks, and qualitative or model-based assessments.

Deterministic evaluation is particularly useful when expected behavior can be expressed as exact rules, while qualitative evaluation is more appropriate for subjective aspects such as relevance, explanation quality, and usefulness.

Based on these principles, the Research Scout Agent uses a combination of automated and qualitative evaluation.

**Automated Evaluation**

The `evaluation.py` script runs predefined research requests and checks:

- Whether the extracted constraints match the expected constraints.
- Whether the agent returns a paper when one is expected.
- Whether returned papers satisfy publication-year constraints.
- Whether returned papers satisfy citation-count constraints.
- Whether returned papers contain the required source metadata, including title, authors, citation source, and URL.
- Whether execution errors or API rate-limit retries occur.

Results are exported to `evaluation_results.csv` for inspection and documentation.

**Qualitative Evaluation**

The returned papers and explanations are also reviewed to assess:

- Relevance to the requested research topic.
- Whether explanations clearly describe the selected paper's contribution.
- Whether the explanations justify the numerical constraints.
- Potential hallucinations or unsupported claims.

This combination was chosen because numerical correctness can be verified reliably using Python, while research relevance and explanation usefulness require additional judgment.

The project uses a custom Python evaluation script rather than the Pydantic Evals framework itself, but follows the same general principles of predefined test cases and explicit evaluation criteria.

**Reference:**

- [Pydantic Evals — Evaluators Overview](https://pydantic.dev/docs/ai/evals/evaluators/overview/)

### Evaluation Results

The Research Scout Agent was initially evaluated using 10 research requests covering different publication-year constraints, citation-count constraints, approximate citation matching, unrestricted searches, and impossible requirements.

All 10 cases passed during the final baseline evaluation run.

Two additional cases were subsequently executed separately to evaluate ambiguous research requests, bringing the total number of tested scenarios to 12. Of these additional cases, one passed all automated checks, while the other failed the source metadata completeness check.

The original 10-case results are preserved in `evaluation_results.csv`, while the additional results are recorded in `evaluation_case_11.csv` and `evaluation_case_12.csv`.

The baseline evaluation was performed before the two additional ambiguous-request cases were added. Running --all with the current evaluation script executes all 12 cases.

The evaluation was executed using:

`python evaluation.py --all --delay 30`

**Results:**

- **10/10** evaluation cases completed successfully.
- **10/10** requests had correctly extracted research constraints.
- **9/9** recommended papers satisfied the numerical constraints.
- **1/1** impossible-constraint request correctly returned no matching paper.
- **0** runtime errors and **0** rate-limit retries occurred during the final evaluation.

The agent retrieved research metadata from OpenAlex and validated publication years and citation counts using deterministic Python logic.

The baseline evaluation measured constraint extraction, numerical validity, expected result availability, and execution errors. Source metadata completeness was added as an additional automated check for the subsequent ambiguous-request tests.

### Qualitative Evaluation

In addition to the automated checks, the returned papers and explanations were reviewed qualitatively.

**Relevance:** The selected papers generally matched their requested research topics. For example, the transformer architecture request returned *Attention Is All You Need* (2017), while the retrieval-augmented generation request returned *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* (2020). Some broader requests returned papers focused on specialized applications rather than general introductions to the subject.

**Constraint Satisfaction:** All nine returned papers satisfied their publication-year and citation-count requirements. The impossible-constraint request correctly returned no matching paper.

**Hallucination Prevention:** The research agent selects papers using an index referencing the candidates retrieved from OpenAlex. The application then returns the original metadata, including the title, authors, publication year, citation count, and URL, rather than relying on language-model-generated paper information.

No fabricated paper metadata was identified in the final 10-case evaluation. However, the explanations are generated by the language model and are not independently fact-checked against the full papers. Therefore, hallucinations or unsupported interpretations cannot be completely ruled out.

**Explanation Quality:** The explanations generally identified the paper's contribution, its relevance to the requested topic, and how it satisfied the numerical constraints. Their usefulness was assessed qualitatively rather than through an automated scoring system.

**Tool Usage:** The research agent is instructed to call the custom `search_research_papers` tool once per research request. The tool caches retrieved candidates within the current agent run to avoid repeated OpenAlex API requests.

The constraint extraction agent runs separately before the research agent begins its search.

The current evaluation does not record the exact number of tool calls made during each run. Therefore, tool usage is described based on the implemented workflow rather than measured call-frequency statistics. Recording tool calls would be a useful future improvement.

### Ambiguous Requests

Two additional evaluation cases were executed to examine how the agent handles research requests containing vague or approximate constraints.

**Case 11 — Approximate Publication Year**

Prompt: "Find a paper about machine learning published around 2020."

The agent correctly extracted the topic without inventing an exact publication-year constraint. It returned *Introduction to Machine Learning* (2019), which is reasonably close to the requested year.

However, the evaluation failed because the returned paper did not satisfy the source metadata completeness check. The title, publication year, citation count, citation source, and URL were present, but the author metadata appears to have been missing.

**Case 12 — Vague Citation Requirements**

Prompt: "Find a recent, highly cited paper about artificial intelligence."

The agent correctly extracted the topic without inventing numerical constraints. It returned *Artificial Intelligence in Service* (2018), with 5,228 citations according to OpenAlex.

The automated evaluation passed, but the qualitative assessment identified a limitation: although the paper was highly cited, a publication from 2018 may not reasonably be considered recent in 2026.

**Observations**

Both cases extracted the expected structured constraints and returned papers satisfying the numerical checks. However, the tests demonstrated that:

- Ambiguous language is not always fully represented by the current constraint model.
- The absence of explicit numerical constraints can allow results that only partially match the user's intent.
- Source metadata completeness can vary between retrieved publications.

The automated checks validate constraint extraction, numerical correctness, and source metadata completeness. The interpretation of ambiguous language is assessed qualitatively.

Future improvements could include support for approximate publication-year ranges, relative dates, citation thresholds for vague terms, and stronger handling of incomplete metadata.

### Evaluation Limitations

Earlier evaluation runs encountered Groq structured-output parsing errors and API rate limits. Changing the research agent to return plain-text selections improved reliability, resulting in a successful final evaluation run.

The agent may also select papers from specialized application domains or publication types other than conventional research articles. Additionally, citation counts can change over time, and the evaluation does not independently verify every claim in the generated explanations.

Detailed baseline results are available in evaluation_results.csv. The additional ambiguous-request results are available in evaluation_case_11.csv and evaluation_case_12.csv

## Limitations

- Search results depend on the availability and quality of OpenAlex metadata.
- The language model may occasionally misunderstand ambiguous requests.
- Only a limited number of search results are retrieved for each request.
- Groq API usage is subject to rate limits.

## Reflection

During development, one of the main challenges was obtaining reliable structured output from the Groq-hosted language model.

The initial implementation required the research agent to return structured Pydantic objects. However, some requests caused output-parsing errors, preventing otherwise valid searches from completing.

To address this, the research agent was changed to return a simpler plain-text response containing a selected paper index and an explanation. Python then parses the response, retrieves the selected paper from the original OpenAlex candidates, and validates its numerical constraints.

This approach improved reliability while preserving structured data models for research constraints and final results.

Another challenge was working within Groq's API rate limits. The evaluation script includes delays between requests and retry handling for rate-limit errors.

The final evaluation completed all 10 test cases successfully without runtime errors or rate-limit retries.

**Possible Future Improvements**

- Improve paper ranking to prioritize more directly relevant research.
- Allow users to specify publication types, such as journal articles or conference papers.
- Add automated checks for explanation accuracy and relevance.
- Support additional research databases beyond OpenAlex.
- Improve handling of ambiguous or incomplete research requests.

Overall, the project demonstrates how PydanticAI agents can combine language-model reasoning with external research tools and deterministic validation to produce more reliable research recommendations.

## Contributions

This project was completed individually.

All components, including the PydanticAI agents, OpenAlex API integration, constraint validation, automated tests, evaluation framework, and documentation, were implemented as part of this individual assignment.