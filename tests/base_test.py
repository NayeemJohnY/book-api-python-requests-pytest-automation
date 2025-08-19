"""Base Test Module"""

import pytest

from helpers.api_client import APIClient


class BaseTest:
    """Base Test Class"""

    client: APIClient

    @pytest.fixture(scope="class", autouse=True)
    def init_api_client(self, request, api_client):
        """Class scope fixture to initialize client with API Client"""
        request.cls.client = api_client
