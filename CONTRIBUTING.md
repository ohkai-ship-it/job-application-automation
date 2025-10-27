# Contributing

Thanks for your interest in improving Job Application Automation!

## Branching model
- Base branch: `develop`
- Feature branches: `feature/<short-name>`
- Bugfix branches: `fix/<short-name>`
- Use PRs for all changes; link issues when possible.

## Development workflow
1. Create a virtual environment and install deps
2. Write or update tests (aim for fast, deterministic tests)
3. Run the test suite locally
4. Commit with clear messages (imperative style)
5. Open a PR to `develop`

## Testing
- Run tests:
  - VS Code: Task "Run tests"
  - CLI: `pytest -q`
- Prefer unit tests for logic and small integration tests for flows
- If adding public behavior, include tests to cover it

## Code style
- Python 3.8+
- Type hints where practical
- Prefer small, composable functions
- Use `src/utils/logging.get_logger` instead of `print`
- Handle errors with meaningful exceptions (see `src/utils/errors.py`)

## Secrets and credentials
- Never commit secrets or API keys
- Use `config/.env` for local development
- Ensure tests and logs never print sensitive data; use masking helpers

## Commits and PRs
- Keep PRs focused; small PRs are easier to review
- Include a short summary of changes and testing notes
- Link to related issues or TODO items

## Reporting bugs
- Provide steps to reproduce, expected vs actual, and logs (with sensitive data removed)
- Include relevant error events from `output/errors` if available
