# Book API Python Requests Pytest Automation

A robust, maintainable, and DRY API test automation framework for a Book API using Python, pytest, and requests.

[![Code Analysis](https://github.com/NayeemJohnY/book-api-python-requests-pytest-automation/actions/workflows/code_analysis.yml/badge.svg)](https://github.com/NayeemJohnY/book-api-python-requests-pytest-automation/actions/workflows/code_analysis.yml) [![Test Execution](https://github.com/NayeemJohnY/book-api-python-requests-pytest-automation/actions/workflows/test-execution.yml/badge.svg)](https://github.com/NayeemJohnY/book-api-python-requests-pytest-automation/actions/workflows/test-execution.yml)

## Features
 - **Custom APIClient**: Centralized HTTP client (`helpers/api_client.py`) with:
     - Built-in retry logic for transient errors (HTTP 429, 5xx) using urllib3's `Retry`.
     - Logging of all requests, responses, and retry attempts (INFO/DEBUG level).
     - Automatic use of `Retry-After` header for backoff.
     - URL building and session management.
 - **Reusable Validators**: Assertion helpers (`helpers/validator.py`) for:
     - Status code validation with logging on pass/fail.
     - Error message and book response validation.
     - All assertions log both pass and fail for traceability.
 - **Pytest Fixtures**: Clean setup/teardown in `conftest.py` and `BaseTest.py`:
     - Session/module/class-scoped fixtures for API client and test data.
     - DRY test setup using base classes and autouse fixtures.
 - **Parameterization**: Use of `@pytest.mark.parametrize` for edge cases and error scenarios.
 - **Parallel Test Execution**: Supports pytest-xdist for parallel test runs by file/module:
     - `dist=loadfile` ensures all tests in a file run sequentially, files run in parallel.
     - Test data is made unique per worker to avoid collisions.
 - **Comprehensive Logging**:
     - All requests, responses, assertions, and retries are logged.
     - Logging configuration in `pytest.ini` supports both CLI and file output.
     - DEBUG/INFO logs available in log file; INFO logs in CLI (with xdist, some logs may only appear in file).
 - **Test Reports**: Generates HTML reports with pytest-html for easy review.
 - **Dependency Management**: Handles test dependencies and ordering with pytest-dependency.

## Project Structure
```
    book-api-pytest-automation/
    ├── helpers/
    │   ├── api_client.py               # Custom API client with retry and logging
    │   └── validator.py                # Assertion and validation helpers
    │
    ├── tests/
    │   ├── BaseTest.py                 # Base test class with client fixture
    │   ├── test_create_book.py
    │   ├── test_update_book.py
    │   ├── test_delete_book.py
    │   └── test_get_book.py
    │  
    ├── .pylintrc                       # pylint overrides
    ├── conftest.py                     # Global fixtures and setup
    ├── pytest.ini                      # Pytest configuration
    └── requirements.txt                # Python dependencies

```

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Book API Server
Ensure your Book API (Node.js or other) is running at `http://localhost:3000`.

### 3. Run Tests
```bash
pytest
```

### 4. Run Tests in Parallel
```bash
pytest -n auto  --dist loadfile # or -n 4 for 4 workers
```


## Key Files

- **helpers/api_client.py**: Custom requests.Session subclass with retry, logging, and URL helpers.
- **helpers/validator.py**: Assertion helpers for status codes, error messages, and book validation.
- **conftest.py**: Global fixtures for API client and test setup.
- **tests/BaseTest.py**: Base class for all test classes, injects API client.
- **tests/test_*.py**: Test modules for create, update, delete, and get book scenarios.
- **pytest.ini**: Pytest configuration (logging, parallelism, test discovery, reporting).

## Best Practices
- **DRY Principle**: Use helpers and fixtures to avoid code duplication.
- **Parameterize**: Use `@pytest.mark.parametrize` for edge cases and error scenarios.
- **Logging**: All requests, responses, and assertions are logged for traceability.
- **Retry Logic**: Built-in retry for transient HTTP errors (429, 5xx) with logging.
- **Parallel Safety**: Test data is made unique per worker for parallel runs.
- **Test Dependencies**: Use `pytest-dependency` for ordered/conditional tests.

## Example Test
```python
class TestCreateBook(BaseTest):
    HEADERS = {"authorization": "Bearer user-token"}

    def test_should_create_book_when_title_and_author_are_valid(self):
        book = {"title": "New Book", "author": "Author"}
        response = self.client.post(self.client.build_url(), json=book, headers=self.HEADERS)
        validator.validate_status_code(response, 201)
        validator.validate_response_book(response, book)
```

## Troubleshooting
- **Connection errors**: Ensure the Book API server is running at the correct URL.
- **Parallel test issues**: Make sure test data is unique per worker or run tests serially.
- **HTML report not generated**: Ensure `pytest-html` is installed and use the `--html` option.
---
