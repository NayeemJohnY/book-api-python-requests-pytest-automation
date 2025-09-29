"""
Performance Testing Configuration
Add this to pytest.ini to support mixed testing
"""

# Add to your pytest.ini [pytest] section:
# markers =
#     performance: marks tests as performance tests
#     load: marks tests as load tests
#     stress: marks tests as stress tests

# Example usage in test files:
# @pytest.mark.performance
# def test_api_performance():
#     # Your test code here
#     pass
