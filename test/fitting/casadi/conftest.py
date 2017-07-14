"""
"""
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest


@pytest.fixture
def plot(request):
    return request.config.getoption("--plot")
