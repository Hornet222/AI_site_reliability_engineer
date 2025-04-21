# AI Site Reliability Engineer

An intelligent SRE assistant that uses the ReAct (Reason + Act) pattern to monitor and analyze GitHub repositories for potential reliability and security issues.

## Features

- Monitors recent code changes and assesses their potential impact
- Tracks security alerts (both code scanning and secret scanning)
- Provides risk assessment and actionable recommendations
- Uses ReAct pattern for intelligent decision-making
- Supports both OpenAI and Anthropic LLMs
- Integrates with GitHub's API through MCP server

## Prerequisites

1. Python 3.8 or higher
2. Node.js and npm (for GitHub MCP server)
3. API keys for chosen LLM provider (OpenAI or Anthropic)
4. GitHub Personal Access Token with appropriate permissions:
   - `repo` (full repository access)
   - `security_events` (for security alerts)

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd ai-site-reliability-engineer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure your settings:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` file with your:
   - LLM provider choice and API key
   - GitHub personal access token
   - Repository details
   - Logfire token (optional, for logging)

## Configuration

The application can be configured through environment variables in the `.env` file:

```ini
# LLM Configuration
LLM_MODEL=claude-3-5-sonnet-latest # or anthropic:claude-3-opus-20240229
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub Configuration
GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here
GITHUB_OWNER=your_github_username_here
GITHUB_REPO=your_repository_name_here
```

## Usage

Run the SRE agent:

```bash
python src/agents/sre_agent.py
```

The agent will:
1. Connect to the specified GitHub repository
2. Analyze recent commits and their potential impact
3. Check for security alerts
4. Generate a comprehensive report including:
   - Code changes analysis
   - Security alerts
   - Risk assessment
   - Actionable recommendations

## Sample Output

```
Analyzing repository: owner/repo

SRE Insight Report
==================================================
Repository: owner/repo

Recent Code Changes:
- Commit: a1b2c3d4
  Author: developer@example.com
  Impact Score: 0.75
  Message: Updated authentication middleware

Security Alerts:
- Alert #123
  Severity: HIGH
  State: open
  Description: Potential SQL injection vulnerability

Risk Assessment:
Recent authentication changes could impact system security...

Recommendations:
- Review authentication middleware changes
- Add additional test coverage
- Update security scanning rules
```

## Architecture

The application uses:
- PydanticAI for the agent framework
- ReAct pattern for intelligent decision-making
- GitHub MCP server (via npx) for repository interaction
- Pydantic models for structured data handling
- Async/await for efficient API interactions

### ReAct Pattern Implementation

The agent follows the ReAct (Reason + Act) pattern:
1. **Reason**: Analyzes current state and decides next action
2. **Act**: Executes chosen action using available tools
3. **Observe**: Processes results and updates understanding
4. **Repeat**: Continues until sufficient information is gathered

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Testing

The project uses pytest for testing. Tests are located in the `tests/` directory.

### Running Tests

1. Install test dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run all tests:
   ```bash
   pytest
   ```

3. Run tests with coverage report:
   ```bash
   pytest --cov=src --cov-report=html
   ```
   This will generate a coverage report in the `htmlcov` directory.

4. Run specific test file:
   ```bash
   pytest tests/test_sre_agent.py
   ```

### Test Structure

The tests cover:
- Individual tool functions (commits, security alerts, file changes)
- Complete SRE insight generation
- Error handling
- Model validation
- Edge cases

### Mocking

The tests use pytest's fixtures and unittest.mock to mock:
- GitHub MCP server responses
- API calls
- External dependencies

This ensures tests are:
- Fast and reliable
- Independent of external services
- Predictable in their behavior

## License

MIT License - see LICENSE file for details 