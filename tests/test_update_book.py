"""Update Book Test Module"""

import pytest
import allure
from helpers import validator
from tests.base_test import BaseTest


@allure.epic("Book Management")
@allure.feature("Update Book")
@allure.severity(allure.severity_level.NORMAL)
class TestUpdateBook(BaseTest):
    """Update Book Test class"""

    book_id: str
    HEADERS = {"authorization": "Bearer user-token"}

    @pytest.fixture(scope="class", autouse=True)
    def create_book_before_update_book_test(self, init_api_client):
        """Create a book to be used for update tests."""
        book = {
            "title": "PUT API Test Book Title",
            "author": "PUT API Test Book Author",
        }
        response = self.client.post(
            self.client.build_url(), json=book, headers=self.HEADERS
        )
        validator.validate_status_code(response, 201)
        validator.validate_response_book(response, book)
        self.__class__.book_id = response.json()["id"]

    def update_and_validate(
        self, update, expected_status=200, expected_message=None, book_id=None
    ):
        """Helper to update a book and validate the response."""
        if book_id is None:
            book_id = self.book_id
        response = self.client.put(
            self.client.build_url(f"/{book_id}"), json=update, headers=self.HEADERS
        )
        validator.validate_status_code(response, expected_status)
        if expected_status == 200:
            return response.json()
        if expected_message:
            validator.validate_error_message(response, expected_message)
        return response

    @pytest.mark.parametrize(
        "field,value",
        [
            ("author", "New Author"),
            ("title", "New Title"),
        ],
    )
    @allure.title("Should update book author or title")
    def test_should_update_book_author_or_title(self, field, value):
        """Test updating author or title of a book."""
        response_book = self.update_and_validate({field: value})
        validator.assert_equals(
            response_book["id"], self.book_id, "PUT API Response Book ID should match"
        )
        validator.assert_equals(
            response_book[field], value, f"PUT API Response Book {field} should match"
        )

    @allure.title("Should return 401 when no auth is provided on update book")
    def test_should_return_401_when_no_auth_is_provided_on_update_book(self):
        """Test updating a book without authentication returns 401."""
        response = self.client.put(
            self.client.build_url(f"/{self.book_id}"),
            json={"author": "test 401 author"},
        )
        validator.validate_status_code(response, 401)
        validator.validate_error_message(response, "Unauthorized. No token provided.")

    @allure.title("Should return 404 when book with ID does not exist")
    def test_should_return_404_when_book_with_id_is_not_exists(self):
        """Test updating a non-existent book returns 404."""
        self.update_and_validate(
            {"author": "test 404 Not Found"},
            expected_status=404,
            expected_message="Book not found",
            book_id="12345678",
        )

    @allure.title("Should return 400 when different book ID is given in body")
    def test_should_return_400_when_different_book_id_is_given_in_body(self):
        """Test updating a book with a mismatched ID in the body returns 400."""
        self.update_and_validate(
            {"id": "123456", "author": "test 404 Not Found"},
            expected_status=400,
            expected_message="Updating book ID is not allowed.",
        )

    @allure.title("Should update book when same book ID is given in body")
    def test_should_update_book_when_same_book_id_is_given_in_body(self):
        """Test updating a book when the same book ID is provided in the body."""
        book = {
            "id": self.book_id,
            "author": "Update Book Author with ID in Body",
            "title": "Update Book Title with ID in Body",
        }
        response = self.client.put(
            self.client.build_url(f"/{self.book_id}"), json=book, headers=self.HEADERS
        )
        validator.validate_status_code(response, 200)
        validator.validate_response_book(response, book)
