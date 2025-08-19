"""Get Book Test Module"""

import allure
import pytest

from helpers import validator
from tests.base_test import BaseTest


@allure.epic("Book Management")
@allure.feature("Get Book")
@allure.severity(allure.severity_level.CRITICAL)
class TestGetBook(BaseTest):
    """Get Book Test Class"""

    SEARCH_ENDPOINT = "/search"
    DEFAULT_HEADERS = {"authorization": "Bearer user-token"}
    NOT_FOUND_MESSAGE = "Books not found for search"

    def assert_search_results(self, response, title=None, author=None):
        """Helper to validate search response and its contents"""
        validator.validate_status_code(response, 200)
        books = response.json()
        if title:
            validator.assert_true(
                all(title in book["title"] for book in books),
                f"All books should contain title '{title}'",
            )
        if author:
            validator.assert_true(
                all(author.lower() in book["author"].lower() for book in books),
                f"All books should contain author '{author}'",
            )

    @pytest.fixture(scope="class")
    def get_books(self):
        """Get Test Books fixture"""
        return [
            {"title": f"Book Title {i}", "author": f"Book Author {i}"}
            for i in range(1, 11)
        ]

    @pytest.fixture(scope="class", autouse=True)
    def create_book_before_test(self, init_api_client, get_books):
        """Class scope fixture to create book before Test"""
        for book in get_books:
            response = self.client.post(
                self.client.build_url(), json=book, headers=self.DEFAULT_HEADERS
            )
            validator.validate_status_code(response, 201)
            validator.validate_response_book(response, book)

    @allure.title("Should return books for default page 1")
    def test_should_return_books_for_default_page1(self):
        """Test Should return Book For Default page 1"""
        response = self.client.get(self.client.build_url())
        validator.validate_status_code(response, 200)
        validator.assert_true(
            len(response.json()) >= 10, "Number Of Books should greater or equal to 10"
        )

    @allure.title("Should return books by page number")
    def test_should_return_books_by_page_number(self):
        """Test Should return book by page number"""
        response = self.client.get(self.client.build_url(), params={"page": 2})
        validator.validate_status_code(response, 200)
        validator.assert_true(
            all(book["id"] >= 10 for book in response.json()),
            "Page 2 Book ids should greater than 10",
        )

    @pytest.mark.parametrize(
        "params,expected_count,message",
        [
            ({"limit": 5}, 5, "Books size by limit"),
            ({"limit": 5, "page": 2}, 5, "Page 2 Book ids should be 5"),
            ({"page": 3}, 0, "Books size out of page range should be 0"),
            ({"page": -3}, 0, "Books size with negative page should be 0"),
        ],
    )
    @allure.title("Pagination cases:{message}")
    def test_pagination_cases(self, params, expected_count, message):
        """Test various pagination scenarios"""
        response = self.client.get(self.client.build_url(), params=params)
        validator.validate_status_code(response, 200)
        validator.assert_true(len(response.json()) == expected_count, message)

    @allure.title("Should return books excluding last limit on negative limit")
    def test_should_return_books_excluding_last_limit_on_negative_limit(self):
        """Test Should return book exlcuding last limit on negative limit"""
        response = self.client.get(self.client.build_url(), params={"limit": -3})
        validator.validate_status_code(response, 200)
        validator.assert_true(
            len(response.json()) != 0, "Books size with negative limt should be 0"
        )

    @allure.title("Should return single book by ID")
    def test_should_return_single_book_by_id(self):
        """Test Should return Single Book by ID"""
        response = self.client.get(self.client.build_url("/10"))
        validator.validate_status_code(response, 200)
        validator.assert_equals(response.json()["id"], 10, "Retrieve Book by book ID")

    @allure.title("Should not return book when book ID is invalid string")
    def test_should_not_return_book_when_book_id_is_invalid_string(self):
        """Test should not return book when Book Id is invalid String"""
        response = self.client.get(self.client.build_url("/invalid-string"))
        validator.validate_status_code(response, 404)
        validator.validate_error_message(response, "Book not found")

    @allure.title("Should not return book when book ID does not exist")
    def test_should_not_return_book_when_book_id_not_exists(self):
        """Test Should not return book when book id not exists"""
        response = self.client.get(self.client.build_url("/999999"))
        validator.validate_status_code(response, 404)
        validator.validate_error_message(response, "Book not found")

    @allure.title("Should return all books when book ID is empty")
    def test_should_return_all_books_when_book_id_is_empty(self):
        """Test should return all books when book id is empty"""
        response = self.client.get(self.client.build_url("/"))
        validator.validate_status_code(response, 200)
        validator.assert_true(
            len(response.json()) >= 10, "Number Of Books should greater or equal to 10"
        )

    @allure.title("Should return books containing author")
    def test_should_return_books_contains_author(self):
        """Test should return book contains author"""
        response = self.client.get(
            self.client.build_url(self.SEARCH_ENDPOINT),
            params={"author": "Book Author"},
        )
        self.assert_search_results(response, author="Book Author")

    @allure.title("Should return books containing title")
    def test_should_return_books_contains_title(self):
        """Test should return book contains title"""
        response = self.client.get(
            self.client.build_url(self.SEARCH_ENDPOINT), params={"title": "Book Title"}
        )
        self.assert_search_results(response, title="Book Title")

    @allure.title("Should return books containing title and author")
    def test_should_return_books_contains_title_and_author(self):
        """Test should return book contains title and author"""
        response = self.client.get(
            self.client.build_url(self.SEARCH_ENDPOINT),
            params={"title": "Book Title", "author": "book author"},
        )
        self.assert_search_results(response, title="Book Title", author="book author")

    @allure.title("Should return single book with title and author")
    def test_should_return_single_book_with_title_and_author(self):
        """Test should return single book for author and title"""
        response = self.client.get(
            self.client.build_url(self.SEARCH_ENDPOINT),
            params={"title": "Book Title 7", "author": "book author 7"},
        )
        self.assert_search_results(
            response, title="Book Title 7", author="book author 7"
        )

    @pytest.mark.parametrize(
        "params,status_code,expected_message",
        [
            ({}, 400, "Please provide at least a title or author for search"),
            (
                {"title": "Book Title Not Exits", "author": "book author Not Exits"},
                404,
                NOT_FOUND_MESSAGE,
            ),
            ({"author": "book author Not Exits"}, 404, NOT_FOUND_MESSAGE),
            ({"title": "Book Title Not Exits"}, 404, NOT_FOUND_MESSAGE),
        ],
    )
    @allure.title("Search error cases: {expected_message}")
    def test_search_error_cases(self, params, status_code, expected_message):
        """Test various error scenarios for book search"""
        response = self.client.get(
            self.client.build_url(self.SEARCH_ENDPOINT), params=params
        )
        validator.validate_status_code(response, status_code)
        validator.validate_error_message(response, expected_message)
