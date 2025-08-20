"""Delete Book Test Module"""

import allure
import pytest
from helpers import validator
from tests.base_test import BaseTest


@allure.epic("Book Management")
@allure.feature("Delete Book")
@allure.severity(allure.severity_level.MINOR)
class TestDeleteBook(BaseTest):
    """Delete Book Test class"""

    book_id: str
    ADMIN_HEADERS = {"authorization": "Bearer admin-token"}
    USER_HEADERS = {"authorization": "Bearer user-token"}

    @pytest.fixture(scope="class", autouse=True)
    def test_create_book_before_delete_book_test(self, init_api_client):
        """Create a book to be used for delete tests."""
        book = {
            "title": "Delete API Test Book Title",
            "author": "Delete API Test Book Author",
        }
        response = self.client.post(
            self.client.build_url(), json=book, headers=self.ADMIN_HEADERS
        )
        validator.validate_status_code(response, 201)
        validator.validate_response_book(response, book)
        self.__class__.book_id = response.json()["id"]

    @allure.title("Should return 401 when no auth token provided on delete")
    def test_should_return_401_when_no_auth_token_provided_on_delete(self):
        """Test deleting a book without authentication returns 401."""
        response = self.client.delete(self.client.build_url(f"/{self.book_id}"))
        validator.validate_status_code(response, 401)
        validator.validate_error_message(response, "Unauthorized. No token provided.")

    @allure.title("Should return 403 when user auth token is provided on delete")
    def test_should_return_403_when_user_auth_token_is_provided_on_delete(self):
        """Test deleting a book with a user token returns 403."""
        response = self.client.delete(
            self.client.build_url(f"/{self.book_id}"), headers=self.USER_HEADERS
        )
        validator.validate_status_code(response, 403)
        validator.validate_error_message(response, "Forbidden. Admin access required.")

    @pytest.mark.dependency(name="delete_valid_book")
    @allure.title("Should delete book when book ID is valid")
    def test_should_delete_book_when_book_id_is_valid(self):
        """Test deleting a book with admin token returns 204."""
        response = self.client.delete(
            self.client.build_url(f"/{self.book_id}"), headers=self.ADMIN_HEADERS
        )
        validator.validate_status_code(response, 204)

    @pytest.mark.dependency(depends=["delete_valid_book"])
    @allure.title("Should return 404 when book is already deleted or does not exist")
    def test_should_return_404_when_book_is_already_deleted_or_not_exists(self):
        """Test deleting a book that is already deleted or does not exist returns 404."""
        response = self.client.delete(
            self.client.build_url(f"/{self.book_id}"), headers=self.ADMIN_HEADERS
        )
        validator.validate_status_code(response, 404)
        validator.validate_error_message(response, "Book not found")
