# Performance Testing Guide

## Overview
This project now supports Locust performance testing without modifying your existing test functions.

## Quick Start

### 1. Install Locust
```bash
pip install locust
```

### 2. Run Simple Load Test
```bash
# Simple configuration (recommended for beginners)
locust -f performance/locust_config.py --host=http://localhost:3000

# Advanced configuration (uses existing test logic)
locust -f performance/advanced_locust.py --host=http://localhost:3000
```

### 3. Open Web UI
- Open browser to http://localhost:8089
- Set number of users (e.g., 10)
- Set spawn rate (e.g., 2 users/second)
- Click "Start swarming"

## Files Created

### `performance/scenarios.py`
- Wraps your existing APIClient and validator logic
- Provides reusable test scenarios for performance testing
- Can be used with any performance testing tool (not just Locust)

### `performance/locust_config.py`
- Simple Locust configuration
- Easy to understand and modify
- Good for basic load testing

### `performance/advanced_locust.py`
- Uses your existing APIClient and validation logic
- Integrates with your helper functions
- More comprehensive test scenarios

### `locustfile.py`
- Complete Locust configuration at project root
- Can be run directly with: `locust --host=http://localhost:3000`

## Command Line Usage

### Basic Commands
```bash
# Run with web UI
locust -f performance/locust_config.py --host=http://localhost:3000

# Run headless (no web UI)
locust -f performance/locust_config.py --host=http://localhost:3000 --headless -u 10 -r 2 -t 60s

# Run with specific file
locust -f locustfile.py --host=http://localhost:3000
```

### Parameters
- `-u` or `--users`: Number of concurrent users
- `-r` or `--spawn-rate`: Rate to spawn users (users per second)
- `-t` or `--run-time`: Stop after specified time (e.g., 60s, 5m, 1h)
- `--headless`: Run without web UI
- `-f`: Specify locust file

## Test Scenarios Included

1. **GET /api/books** - Most frequent operation (weight: 5)
2. **GET /api/books?page=X&limit=Y** - Pagination testing (weight: 3)
3. **GET /api/books/{id}** - Single book retrieval (weight: 2)
4. **GET /api/books/search** - Search functionality (weight: 2)
5. **POST /api/books** - Book creation (weight: 1)
6. **PUT /api/books/{id}** - Book updates (weight: 1)
7. **DELETE /api/books/{id}** - Book deletion (weight: 1)
8. **Authentication scenarios** - Various auth tests (weight: 1)

## Integration with Existing Code

The performance tests use your existing:
- `helpers/api_client.py` - Your custom APIClient
- `helpers/validator.py` - Your validation functions
- Authentication headers from your tests
- Error handling patterns

## Advanced Usage

### Custom Test Scenarios
```python
from performance.scenarios import BookAPITestScenarios

# Create test scenarios instance
scenarios = BookAPITestScenarios()

# Use existing test logic
response = scenarios.get_all_books()
response, book_id = scenarios.create_test_book()
response = scenarios.search_books("title", "author")
```

### Performance Metrics
Locust automatically tracks:
- Response times (min, max, average, percentiles)
- Requests per second
- Failure rates
- Response sizes
- User concurrency

## Best Practices

1. **Start small**: Begin with 5-10 users
2. **Gradual increase**: Increase load gradually
3. **Monitor resources**: Watch CPU, memory, database
4. **Test realistic scenarios**: Use production-like data
5. **Run multiple tests**: Different load patterns

## Troubleshooting

### Common Issues
1. **Import errors**: Make sure `pip install locust` is run
2. **Connection errors**: Ensure your API server is running on localhost:3000
3. **High error rates**: Check server capacity and reduce user count

### Server Setup
```bash
# Make sure your API server is running
cd path/to/your/nodejs/server
npm start

# In another terminal, run performance tests
cd path/to/this/project
locust -f performance/locust_config.py --host=http://localhost:3000
```

## Results Analysis

After running tests, analyze:
- **Response time percentiles** (50%, 95%, 99%)
- **Requests per second** capability
- **Error rates** under load
- **Resource utilization** (if monitoring server)

## Continuous Integration

Add to your CI pipeline:
```bash
# Run automated performance test
locust -f performance/locust_config.py --host=http://localhost:3000 --headless -u 50 -r 5 -t 5m --html=performance-report.html
```
