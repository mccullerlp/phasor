"""
"""
import pytest


@pytest.fixture
def plot(request):
    return request.config.option.plot
