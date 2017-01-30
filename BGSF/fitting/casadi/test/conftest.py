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


@pytest.fixture
def plot(request):
    #return request.config.getoption("--plot")
    return False
