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

## Prerequisites

Before running the application, make sure you have:

- Python 3.14 or a compatible version.
- Git (for cloning the repository).
- A Groq API key.
- An OpenAlex API key.

API keys can be obtained from:

- [Groq Console](https://console.groq.com/)
- [OpenAlex](https://openalex.org/)

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

## Running Tests

The project includes automated tests for constraint validation and result verification.

Run all tests using:

```bash
python -m pytest -v
```

These tests check that publication-year and citation-count constraints are handled correctly and that unverified papers are rejected.

### Main Components

**`main.py`**

Provides the command-line interface and displays research results.

**`constraint_extractor.py`**

Uses a language model to extract structured research constraints from natural-language requests.

**`agent.py`**

Defines the research agent, integrates the OpenAlex search tool, and coordinates result verification.

**`models.py`**

Defines the structured Pydantic models used throughout the application.

**`research_tool.py`**

Queries OpenAlex, retrieves research metadata, and applies API filters.

**`validation.py`**

Checks publication-year and citation-count constraints using deterministic Python logic.

**`verification.py`**

Verifies that a recommended paper matches the retrieved OpenAlex data and the extracted constraints.

## Evaluation

Evaluation results and observations will be added after testing the agent with different research requests.

## Limitations

- Search results depend on the availability and quality of OpenAlex metadata.
- Citation counts can change over time.
- The language model may occasionally misunderstand ambiguous requests.
- Only a limited number of search results are retrieved for each request.
- Groq API usage is subject to rate limits.