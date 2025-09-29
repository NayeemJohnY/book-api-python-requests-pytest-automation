"""
Advanced Locust Configuration using existing test scenarios
This integrates with your existing APIClient and validation logic
"""

try:
    from locust import HttpUser, task, between, events
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    from performance.scenarios import BookAPITestScenarios
    import random
    import logging

    # Reduce noise from requests logging during load testing
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    class BookAPIAdvancedTest(HttpUser):
        """Advanced load test using existing test scenarios"""

        wait_time = between(1, 5)

        def on_start(self):
            """Initialize test scenarios"""
            self.scenarios = BookAPITestScenarios()
            # Create some initial test data
            for i in range(3):
                self.scenarios.create_test_book(
                    f"user-{self.environment.runner.user_count}-"
                )

        @task(5)
        def load_test_get_books(self):
            """Load test get all books using existing logic"""
            try:
                response = self.scenarios.get_all_books()
                if response and response.status_code == 200:
                    self.environment.events.request_success.fire(
                        request_type="GET",
                        name="/api/books",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    self.environment.events.request_failure.fire(
                        request_type="GET",
                        name="/api/books",
                        response_time=0,
                        exception="Failed response",
                    )
            except Exception as e:
                self.environment.events.request_failure.fire(
                    request_type="GET",
                    name="/api/books",
                    response_time=0,
                    exception=str(e),
                )

        @task(3)
        def load_test_get_book_by_id(self):
            """Load test get book by ID"""
            try:
                response = self.scenarios.get_book_by_id()
                if response and response.status_code in [200, 404]:
                    self.environment.events.request_success.fire(
                        request_type="GET",
                        name="/api/books/{id}",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    self.environment.events.request_failure.fire(
                        request_type="GET",
                        name="/api/books/{id}",
                        response_time=0,
                        exception="Unexpected response",
                    )
            except Exception as e:
                self.environment.events.request_failure.fire(
                    request_type="GET",
                    name="/api/books/{id}",
                    response_time=0,
                    exception=str(e),
                )

        @task(2)
        def load_test_search_books(self):
            """Load test search functionality"""
            try:
                response = self.scenarios.search_books("Test", "Author")
                if response and response.status_code in [200, 404]:
                    self.environment.events.request_success.fire(
                        request_type="GET",
                        name="/api/books/search",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    self.environment.events.request_failure.fire(
                        request_type="GET",
                        name="/api/books/search",
                        response_time=0,
                        exception="Search failed",
                    )
            except Exception as e:
                self.environment.events.request_failure.fire(
                    request_type="GET",
                    name="/api/books/search",
                    response_time=0,
                    exception=str(e),
                )

        @task(1)
        def load_test_create_book(self):
            """Load test book creation"""
            try:
                response, book_id = self.scenarios.create_test_book()
                if response and response.status_code == 201:
                    self.environment.events.request_success.fire(
                        request_type="POST",
                        name="/api/books",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    self.environment.events.request_failure.fire(
                        request_type="POST",
                        name="/api/books",
                        response_time=0,
                        exception="Book creation failed",
                    )
            except Exception as e:
                self.environment.events.request_failure.fire(
                    request_type="POST",
                    name="/api/books",
                    response_time=0,
                    exception=str(e),
                )

        @task(1)
        def load_test_update_book(self):
            """Load test book updates"""
            try:
                response = self.scenarios.update_book()
                if response and response.status_code in [200, 404]:
                    self.environment.events.request_success.fire(
                        request_type="PUT",
                        name="/api/books/{id}",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    self.environment.events.request_failure.fire(
                        request_type="PUT",
                        name="/api/books/{id}",
                        response_time=0,
                        exception="Update failed",
                    )
            except Exception as e:
                self.environment.events.request_failure.fire(
                    request_type="PUT",
                    name="/api/books/{id}",
                    response_time=0,
                    exception=str(e),
                )

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        print("🚀 Starting Advanced Book API Load Test...")
        print("📊 Using existing APIClient and validation logic")
        print("🔧 Test scenarios integrated from pytest project")

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        print("✅ Advanced Load Test completed!")

except ImportError:
    print("⚠️  Locust not installed. Install with: pip install locust")
    print("💡 You can still use the scenarios.py for other performance testing tools")
