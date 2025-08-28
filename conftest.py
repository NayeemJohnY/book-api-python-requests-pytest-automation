"""Global Fixtures"""

import json
import logging
import os
import shutil
from pathlib import Path

import pytest
from _pytest.python import Function
from _pytest.reports import TestReport
from pluggy import Result
from pytest import Session

from helpers.api_client import APIClient

logger = logging.getLogger(__name__)

BASE_URI = "http://localhost:3000"
BASE_PATH = "/api/books"


test_results = {}
test_plan_suite = {}
test_case_mappings = {}
TEMP_TEST_RESULTS_DIR = Path("test-results-tmp")
TEST_PLAN_SUITE_PATH = "test-plan-suite.json"
TEST_RESULTS_PATH = "test-results/test-results-report.json"

with open(TEST_PLAN_SUITE_PATH, encoding="utf-8") as f:
    test_plan_suite = json.load(f)
    test_case_mappings = test_plan_suite["testCases"]


@pytest.fixture(scope="module")
def api_client():
    """API Client Global Fixture"""
    return APIClient(BASE_URI, BASE_PATH)


def collect_test_results(test_name: str, test_params: str, report: TestReport, call=None):
    """
    Collects and aggregates test results for each test case.
    Stores outcome, duration (in ms), and iteration details if test parameters are present.
    """
    def get_outcome():
        if report.outcome == "skipped":
            return "Error"
        return report.outcome.capitalize()
    
    def get_error_message():
        if call and call.excinfo:
            # Get simple exception message from call.excinfo
            exception_type = call.excinfo.typename
            exception_value = str(call.excinfo.value)
            return f"{exception_type}: {exception_value}"
        return ""
        
    test_case_id: str = test_case_mappings[test_name]["testCaseId"]
    # Convert duration to milliseconds
    duration_ms = int(float(report.duration) * 1000)
    error_message = get_error_message()
    new_outcome = get_outcome()
    
    result = test_results.setdefault(
        test_case_id,
        {
            "outcome": new_outcome,
            "durationInMs": 0,
            "comment": f"Test Name: {test_name}",
            "iterationDetails": [],
        },
    )

    if test_params:
        iteration_id = len(result["iterationDetails"]) + 1
        error_message = f"Iteration {iteration_id}: {error_message}" if error_message else error_message
        iteration_result = {
            "id": iteration_id,
            "outcome": new_outcome,
            "durationInMs": duration_ms,
            "errorMessage": error_message,
            "comment": f"DataDriven: Test Parameters: {json.dumps(test_params)}",
        }
        result["iterationDetails"].append(iteration_result)

    result["durationInMs"] += duration_ms
    
    # Update outcome based on current and new results
    current_outcome = result["outcome"]
    # Determine final outcome: same = keep, different = Inconclusive
    if current_outcome != new_outcome:
        result["outcome"] = "Inconclusive"
    
    # Append error messages from all iterations
    if error_message:
        existing_error = result.get("errorMessage", "")
        if existing_error:
            result["errorMessage"] = f"{existing_error}\n{error_message}"
        else:
            result["errorMessage"] = error_message


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Function, call):
    """
    Pytest hook to collect test results after each test call phase.
    Passes test name, parameters, and report to collect_test_results.
    """
    outcome: Result = yield
    report: TestReport = outcome.get_result()
    test_name: str = item.originalname
    test_params = item.callspec.params if hasattr(item, "callspec") else None
    
    # Collect results for call phase (actual test execution)
    if report.when == "call":
        collect_test_results(test_name, test_params, report, call)
    
    # Handle setup failures - mark as error
    elif report.when == "setup" and report.outcome in ["failed", "skipped"]:
        collect_test_results(test_name, test_params, report, call)


def pytest_sessionfinish(session: Session, exitstatus):
    """
    Pytest hook called after the whole test run is complete.
    Cleans up test data and writes aggregated test results to a JSON file.
    """
    workerinput = getattr(session.config, "workerinput", None)

    if workerinput:
        # In a worker process — write partial result
        worker_id = workerinput["workerid"]
        TEMP_TEST_RESULTS_DIR.mkdir(exist_ok=True)
        result_file = TEMP_TEST_RESULTS_DIR / f"{worker_id}.json"
        with open(result_file, "w", encoding="utf-8") as temp_file:
            json.dump(test_results, temp_file, indent=2)
    else:

        client = APIClient(BASE_URI, BASE_PATH)
        res = client.delete(
            client.build_url("/reset"), headers={"authorization": "Bearer admin-token"}
        )

        assert (
            res.status_code == 204
        ), f"Reset failed: {res.status_code} {res.text}"  # nosec

        # In the main process — wait for workers to finish and merge their results
        for temp_file_path in TEMP_TEST_RESULTS_DIR.glob("*.json"):
            with open(temp_file_path, "r", encoding="utf-8") as temp_results_file:
                worker_data = json.load(temp_results_file)
                test_results.update(worker_data)
        report = {
            "testPlanName": test_plan_suite['testPlanName'],
            "testSuiteName": test_plan_suite['testSuiteName'],
            "testResults": test_results
        }

        with open(TEST_RESULTS_PATH, "w", encoding="utf-8") as out:
            json.dump(report, out, indent=4)
            logger.info(
                "Test results report generated successfully: %s", TEST_RESULTS_PATH
            )
        if os.path.isdir(TEMP_TEST_RESULTS_DIR):
            shutil.rmtree(TEMP_TEST_RESULTS_DIR)
