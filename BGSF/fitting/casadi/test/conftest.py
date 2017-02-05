"""
"""
import pytest


@pytest.fixture
def plot(request):
    return request.config.getoption("--plot")
