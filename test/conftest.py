"""
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--plot",
        action="store_true",
        dest='plot',
        help="Have tests update plots (it is slow)",
    )

    parser.addoption("--do-benchmarks", action="store_true",
        help="run slow benchmarking tests")

    parser.addoption("--do-stresstest", action="store_true",
        help="Run slow repeated stress tests")

@pytest.fixture
def plot(request):
    return request.config.getvalue('plot')
    return request.config.option.plot
