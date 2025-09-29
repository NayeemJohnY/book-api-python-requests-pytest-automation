"""
Simple Locust Performance Test Configuration
Run with: locust -f performance/locust_config.py --host=http://localhost:3000
"""

from locust import HttpUser, task, between
import random

# Test data
SAMPLE_BOOKS = [
    {"title": "Performance Test Book 1", "author": "Load Test Author 1"},
    {"title": "Performance Test Book 2", "author": "Load Test Author 2"},
    {"title": "Performance Test Book 3", "author": "Load Test Author 3"},
]

USER_HEADERS = {"authorization": "Bearer user-token"}
ADMIN_HEADERS = {"authorization": "Bearer admin-token"}


class BookAPILoadTest(HttpUser):
    """Simple Locust load test for Book API"""

    wait_time = between(1, 3)

    def on_start(self):
        """Setup method - create some test data"""
        self.created_book_ids = []
        # Create a few books for testing
        for book in SAMPLE_BOOKS:
            response = self.client.post("/api/books", json=book, headers=USER_HEADERS)
            if response.status_code == 201:
                self.created_book_ids.append(response.json().get("id"))

    @task(5)  # Higher weight = more frequent
    def get_all_books(self):
        """Most common operation - get all books"""
        self.client.get("/api/books")

    @task(3)
    def get_books_with_params(self):
        """Get books with pagination"""
        params = {"page": random.randint(1, 3), "limit": random.choice([5, 10, 15])}
        self.client.get("/api/books", params=params)

    @task(2)
    def get_book_by_id(self):
        """Get specific book"""
        book_id = random.choice(self.created_book_ids) if self.created_book_ids else 1
        self.client.get(f"/api/books/{book_id}")

    @task(2)
    def search_books(self):
        """Search for books"""
        search_params = random.choice(
            [
                {"title": "Performance"},
                {"author": "Author"},
                {"title": "Test", "author": "Load"},
            ]
        )
        self.client.get("/api/books/search", params=search_params)

    @task(1)
    def create_book(self):
        """Create new book"""
        book = {
            "title": f"New Book {random.randint(1000, 9999)}",
            "author": f"Author {random.randint(100, 999)}",
        }
        response = self.client.post("/api/books", json=book, headers=USER_HEADERS)
        if response.status_code == 201:
            book_id = response.json().get("id")
            if book_id:
                self.created_book_ids.append(book_id)

    @task(1)
    def update_book(self):
        """Update existing book"""
        if self.created_book_ids:
            book_id = random.choice(self.created_book_ids)
            update_data = {"title": f"Updated Title {random.randint(1000, 9999)}"}
            self.client.put(
                f"/api/books/{book_id}", json=update_data, headers=USER_HEADERS
            )

    @task(1)
    def delete_book(self):
        """Delete book (admin only)"""
        if self.created_book_ids:
            book_id = self.created_book_ids.pop()
            self.client.delete(f"/api/books/{book_id}", headers=ADMIN_HEADERS)
