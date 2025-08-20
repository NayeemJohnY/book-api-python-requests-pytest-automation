"""Create Book Test Module"""

import allure
import pytest

from helpers import validator
from tests.base_test import BaseTest


@allure.epic("Book Management")
@allure.feature("Create Book")
@allure.severity(allure.severity_level.CRITICAL)
class TestCreateBook(BaseTest):
    """Create Book Test Class"""

    HEADERS = {"authorization": "Bearer user-token"}

    def create_and_validate_book(
        self, book, expected_status=201, expected_message=None
    ):
        """Helper to create a book and validate the response."""
        response = self.client.post(
            self.client.build_url(), json=book, headers=self.HEADERS
        )
        validator.validate_status_code(response, expected_status)
        if expected_status == 201:
            validator.validate_response_book(response, book)
        elif expected_message:
            validator.validate_error_message(response, expected_message)
        return response

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title("Should create book when title and author are valid")
    def test_should_create_book_when_title_and_author_are_valid(self):
        """Test creating a book with valid title and author."""
        book = {
            "title": "New Book POST API Title",
            "author": "New Book POST API Author",
        }
        self.create_and_validate_book(book)

    @pytest.mark.negative
    @pytest.mark.regression
    @allure.title("Should reject duplicate book creation")
    def test_should_reject_duplicate_book_creation(self):
        """Test duplicate book creation returns 409."""
        book = {
            "title": "New Book POST API Title",
            "author": "New Book POST API Author",
        }
        self.create_and_validate_book(
            book,
            expected_status=409,
            expected_message="A book with the same title and author already exists",
        )

    @pytest.mark.regression
    @allure.title("Should create book when title is different for same author")
    def test_should_create_book_when_title_is_different_for_same_author(self):
        """Test creating a book with a different title for the same author."""
        book = {
            "title": "New Book POST API Title Different",
            "author": "New Book POST API Author",
        }
        self.create_and_validate_book(book)

    @pytest.mark.regression
    @allure.title("Should create book when author is different for same book")
    def test_should_create_book_when_author_is_different_for_same_book(self):
        """Test creating a book with a different author for the same title."""
        book = {
            "title": "New Book POST API Title Different",
            "author": "New Book POST API Author Different",
        }
        self.create_and_validate_book(book)

    @pytest.mark.negative
    @pytest.mark.regression
    @allure.title("Should return 401 when no auth token provided")
    def test_should_return_401_when_no_auth_token_provided(self):
        """Test creating a book without authentication returns 401."""
        book = {"title": "Error 401 Test Title", "author": "Error 401 Test Author"}
        response = self.client.post(self.client.build_url(), json=book)
        validator.validate_status_code(response, 401)
        validator.validate_error_message(response, "Unauthorized. No token provided.")

    @pytest.mark.negative
    @pytest.mark.regression
    @pytest.mark.parametrize(
        "payload,expected_message",
        [
            ({}, "Both title and author are required."),
            ({"author": "author only test"}, "Both title and author are required."),
            ({"title": "title only test"}, "Both title and author are required."),
        ],
    )
    @allure.title("Should reject book with missing fields {expected_message}")
    def test_should_reject_book_with_missing_fields(self, payload, expected_message):
        """Test creating a book with missing fields returns 400."""
        self.create_and_validate_book(
            payload, expected_status=400, expected_message=expected_message
        )

    @pytest.mark.negative
    @pytest.mark.regression
    @allure.title("Should reject book creation with client-provided ID")
    def test_should_reject_book_creation_with_client_provided_id(self):
        """Test creating a book with a client-provided ID returns 400."""
        book = {
            "id": "122233",
            "title": "Client provided Book ID Title",
            "author": "Client provided Book Author",
        }
        self.create_and_validate_book(
            book,
            expected_status=400,
            expected_message="ID must not be provided when creating a book",
        )
