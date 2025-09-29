"""
Performance Test Scenarios using existing test logic
This module provides functions that can be imported into Locust or other performance testing tools
"""

import random
from helpers.api_client import APIClient
from helpers import validator


class BookAPITestScenarios:
    """Test scenarios that wrap existing test logic for performance testing"""

    def __init__(self, base_url="http://localhost:3000", base_path="/api/books"):
        self.client = APIClient(base_url, base_path)
        self.user_headers = {"authorization": "Bearer user-token"}
        self.admin_headers = {"authorization": "Bearer admin-token"}
        self.created_books = []

    def create_test_book(self, suffix=""):
        """Create a book using existing test logic"""
        book = {
            "title": f"Load Test Book Title {suffix}{random.randint(1000, 9999)}",
            "author": f"Load Test Author {suffix}{random.randint(100, 999)}",
        }

        try:
            response = self.client.post(
                self.client.build_url(), json=book, headers=self.user_headers
            )

            if response.status_code == 201:
                # Use existing validator logic
                validator.validate_status_code(response, 201)
                validator.validate_response_book(response, book)
                book_id = response.json()["id"]
                self.created_books.append(book_id)
                return response, book_id

            return response, None

        except Exception as e:
            print(f"Error creating book: {e}")
            return None, None

    def get_all_books(self):
        """Get all books scenario"""
        try:
            response = self.client.get(self.client.build_url())
            validator.validate_status_code(response, 200)
            return response
        except Exception as e:
            print(f"Error getting books: {e}")
            return None

    def get_book_by_id(self, book_id=None):
        """Get book by ID scenario"""
        if book_id is None and self.created_books:
            book_id = random.choice(self.created_books)
        elif book_id is None:
            book_id = random.randint(1, 10)

        try:
            response = self.client.get(self.client.build_url(f"/{book_id}"))
            # Accept both 200 and 404 as valid responses
            if response.status_code in [200, 404]:
                return response
            else:
                validator.validate_status_code(response, 200)
                return response
        except Exception as e:
            print(f"Error getting book {book_id}: {e}")
            return None

    def search_books(self, title=None, author=None):
        """Search books scenario"""
        params = {}
        if title:
            params["title"] = title
        if author:
            params["author"] = author

        if not params:
            params = {"title": "Test"}  # Default search

        try:
            response = self.client.get(self.client.build_url("/search"), params=params)
            # Accept both 200 and 404 as valid responses for search
            if response.status_code in [200, 404]:
                return response
            else:
                validator.validate_status_code(response, 200)
                return response
        except Exception as e:
            print(f"Error searching books: {e}")
            return None

    def update_book(self, book_id=None, update_data=None):
        """Update book scenario"""
        if book_id is None and self.created_books:
            book_id = random.choice(self.created_books)
        elif book_id is None:
            return None

        if update_data is None:
            update_data = {"title": f"Updated Title {random.randint(1000, 9999)}"}

        try:
            response = self.client.put(
                self.client.build_url(f"/{book_id}"),
                json=update_data,
                headers=self.user_headers,
            )
            # Accept both 200 and 404 as valid responses
            if response.status_code in [200, 404]:
                return response
            else:
                validator.validate_status_code(response, 200)
                return response
        except Exception as e:
            print(f"Error updating book {book_id}: {e}")
            return None

    def delete_book(self, book_id=None):
        """Delete book scenario - requires admin"""
        if book_id is None and self.created_books:
            book_id = self.created_books.pop(0)
        elif book_id is None:
            return None

        try:
            response = self.client.delete(
                self.client.build_url(f"/{book_id}"), headers=self.admin_headers
            )
            # Accept both 204 and 404 as valid responses
            if response.status_code in [204, 404]:
                return response
            else:
                validator.validate_status_code(response, 204)
                return response
        except Exception as e:
            print(f"Error deleting book {book_id}: {e}")
            return None

    def test_auth_scenarios(self):
        """Test various auth scenarios"""
        scenarios = [
            # Test no auth (should get 401)
            lambda: self.client.post(
                self.client.build_url(), json={"title": "Test", "author": "Test"}
            ),
            # Test user auth for delete (should get 403)
            lambda: self.client.delete(
                self.client.build_url(f"/{random.randint(1, 10)}"),
                headers=self.user_headers,
            ),
        ]

        scenario = random.choice(scenarios)
        try:
            return scenario()
        except Exception as e:
            print(f"Error in auth scenario: {e}")
            return None


def get_performance_test_scenarios():
    """Factory function to get test scenarios instance"""
    return BookAPITestScenarios()
