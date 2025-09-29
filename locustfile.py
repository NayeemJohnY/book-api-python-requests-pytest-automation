"""
Locust Performance Testing for Book API
Uses existing APIClient and test logic without modifying test functions
"""

import random
import logging
from locust import HttpUser, task, between, events
from helpers.api_client import APIClient
from helpers import validator
import requests

# Suppress verbose logs from requests/urllib3 during load testing
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

# Test data for load testing
BOOK_TITLES = [
    "The Great Gatsby",
    "To Kill a Mockingbird",
    "1984",
    "Pride and Prejudice",
    "The Catcher in the Rye",
    "Lord of the Flies",
    "Of Mice and Men",
    "Brave New World",
    "The Grapes of Wrath",
    "Fahrenheit 451",
    "Jane Eyre",
    "Wuthering Heights",
    "The Picture of Dorian Gray",
    "Heart of Darkness",
    "The Metamorphosis",
]

AUTHORS = [
    "F. Scott Fitzgerald",
    "Harper Lee",
    "George Orwell",
    "Jane Austen",
    "J.D. Salinger",
    "William Golding",
    "John Steinbeck",
    "Aldous Huxley",
    "Ray Bradbury",
    "Charlotte Brontë",
    "Emily Brontë",
    "Oscar Wilde",
    "Joseph Conrad",
    "Franz Kafka",
]

# Authentication headers
USER_HEADERS = {"authorization": "Bearer user-token"}
ADMIN_HEADERS = {"authorization": "Bearer admin-token"}


class BookAPIUser(HttpUser):
    """Locust User class for Book API performance testing"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Setup method called when user starts"""
        # Initialize API client using existing helper
        self.api_client = APIClient("http://localhost:3000", "/api/books")
        self.created_book_ids = []

        # Create some initial test data
        self.setup_test_data()

    def setup_test_data(self):
        """Create initial books for testing"""
        for i in range(3):
            title = f"{random.choice(BOOK_TITLES)} {random.randint(1000, 9999)}"
            author = random.choice(AUTHORS)
            book = {"title": title, "author": author}

            try:
                response = self.api_client.post(
                    self.api_client.build_url(), json=book, headers=USER_HEADERS
                )
                if response.status_code == 201:
                    book_id = response.json().get("id")
                    if book_id:
                        self.created_book_ids.append(book_id)
            except Exception as e:
                logging.warning(f"Failed to create initial book: {e}")

    @task(3)
    def get_all_books(self):
        """Test GET /api/books - most common operation"""
        with self.client.get("/api/books", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(2)
    def get_books_with_pagination(self):
        """Test GET /api/books with pagination"""
        page = random.randint(1, 3)
        limit = random.choice([5, 10, 15])

        with self.client.get(
            f"/api/books?page={page}&limit={limit}", catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(2)
    def get_book_by_id(self):
        """Test GET /api/books/{id}"""
        if self.created_book_ids:
            book_id = random.choice(self.created_book_ids)
        else:
            book_id = random.randint(1, 10)  # Fallback to random ID

        with self.client.get(f"/api/books/{book_id}", catch_response=True) as response:
            if response.status_code in [200, 404]:  # Both are valid responses
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(2)
    def search_books(self):
        """Test GET /api/books/search"""
        search_params = random.choice(
            [
                {"title": "Book"},
                {"author": "Author"},
                {"title": "Test", "author": "API"},
            ]
        )

        with self.client.get(
            "/api/books/search", params=search_params, catch_response=True
        ) as response:
            if response.status_code in [200, 404]:  # Both are valid responses
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(1)
    def create_book(self):
        """Test POST /api/books - requires authentication"""
        title = f"{random.choice(BOOK_TITLES)} {random.randint(1000, 9999)}"
        author = random.choice(AUTHORS)
        book = {"title": title, "author": author}

        with self.client.post(
            "/api/books", json=book, headers=USER_HEADERS, catch_response=True
        ) as response:
            if response.status_code == 201:
                # Store created book ID for later use
                book_data = response.json()
                if "id" in book_data:
                    self.created_book_ids.append(book_data["id"])
                response.success()
            elif response.status_code == 409:  # Duplicate book
                response.success()  # This is expected behavior
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(1)
    def update_book(self):
        """Test PUT /api/books/{id} - requires authentication"""
        if not self.created_book_ids:
            return

        book_id = random.choice(self.created_book_ids)
        update_data = random.choice(
            [
                {"title": f"Updated {random.choice(BOOK_TITLES)}"},
                {"author": f"Updated {random.choice(AUTHORS)}"},
                {
                    "title": f"Updated Title {random.randint(1000, 9999)}",
                    "author": f"Updated {random.choice(AUTHORS)}",
                },
            ]
        )

        with self.client.put(
            f"/api/books/{book_id}",
            json=update_data,
            headers=USER_HEADERS,
            catch_response=True,
        ) as response:
            if response.status_code in [200, 404]:  # Both are valid responses
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(1)
    def delete_book(self):
        """Test DELETE /api/books/{id} - requires admin authentication"""
        if not self.created_book_ids:
            return

        book_id = (
            self.created_book_ids.pop(0)
            if self.created_book_ids
            else random.randint(1, 100)
        )

        with self.client.delete(
            f"/api/books/{book_id}", headers=ADMIN_HEADERS, catch_response=True
        ) as response:
            if response.status_code in [204, 404]:  # Both are valid responses
                response.success()
            else:
                response.failure(f"Got status code: {response.status_code}")

    @task(1)
    def test_auth_scenarios(self):
        """Test various authentication scenarios"""
        scenarios = [
            # No auth
            ("POST", "/api/books", {"title": "Test", "author": "Test"}, None, [401]),
            # User auth for update
            (
                "PUT",
                f"/api/books/{random.randint(1, 10)}",
                {"title": "Test"},
                USER_HEADERS,
                [200, 404],
            ),
            # User auth for delete (should fail with 403)
            (
                "DELETE",
                f"/api/books/{random.randint(1, 10)}",
                None,
                USER_HEADERS,
                [403, 404],
            ),
        ]

        method, url, json_data, headers, expected_codes = random.choice(scenarios)

        with self.client.request(
            method, url, json=json_data, headers=headers, catch_response=True
        ) as response:
            if response.status_code in expected_codes:
                response.success()
            else:
                response.failure(
                    f"Expected {expected_codes}, got {response.status_code}"
                )


# Event handlers for custom metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test starts"""
    print("🚀 Starting Book API Load Test...")
    print("📚 Test scenarios:")
    print("  - GET all books (most common)")
    print("  - GET books with pagination")
    print("  - GET book by ID")
    print("  - Search books")
    print("  - Create new books")
    print("  - Update existing books")
    print("  - Delete books (admin)")
    print("  - Authentication scenarios")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test stops"""
    print("✅ Book API Load Test completed!")


if __name__ == "__main__":
    # This allows running the locustfile directly for testing
    import subprocess
    import sys

    print("Starting Locust web interface...")
    print("Open http://localhost:8089 in your browser")
    subprocess.run(
        [sys.executable, "-m", "locust", "-f", __file__, "--host=http://localhost:3000"]
    )
