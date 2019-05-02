import pytest

from .context import kafka_connect_healthcheck

test_data = [
    "0.0.1",
]


@pytest.mark.parametrize("test_input", test_data)
def test_get_version(test_input):
    old_version = kafka_connect_healthcheck.version.__version__
    kafka_connect_healthcheck.version.__version__ = test_input
    assert kafka_connect_healthcheck.version.get_version() == test_input
    kafka_connect_healthcheck.version.__version__ = old_version
