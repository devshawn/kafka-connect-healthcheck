import os
import signal
import subprocess
import time

import coverage.data
import pytest
import requests
from requests.exceptions import ConnectionError

from tests import mocks


@pytest.fixture(autouse=True)
def run_backend(cov, request):
    env = os.environ.copy()
    env['COVERAGE_FILE'] = '.coverage.backend'

    try:
        test_environment, mock_name = request.param
        kafka_connect_url = None
        if test_environment.get("HEALTHCHECK_CONNECT_URL") is None:
            kafka_connect_port = setup_mock_kafka_connect_api(mock_name)
            kafka_connect_url = "http://localhost:{}".format(kafka_connect_port)
            env['HEALTHCHECK_CONNECT_URL'] = kafka_connect_url

        for key, value in test_environment.items():
            env[key] = value
            print("\nAdding environment variable: {} --> {}".format(key, value))

        process = generate_subprocess(env, request)
        wait_for_servers_to_be_up(kafka_connect_url)

        yield

        process.send_signal(signal.SIGINT)
        # out, err = process.communicate()
        # request.config.cache.set('logs', err.decode("utf-8"))
        time.sleep(1)

        if is_coverage_on(request):
            write_backend_coverage(cov)

    except AttributeError:
        print("\nNo parameters, ignoring fixture.")
        yield


def generate_subprocess(env, request):
    print()
    if is_coverage_on(request):
        process_args = " ".join(['exec', 'python3', '-m', 'coverage', 'run', '--source', './kafka_connect_healthcheck',
                                 './kafka_connect_healthcheck/main.py']),
    else:
        process_args = " ".join(['exec', 'python3', './kafka_connect_healthcheck/main.py']),
    return subprocess.Popen(
        process_args,
        env=env,
        shell=True,
        stdout=None if os.environ.get("TEST_SHOW_SERVER_LOGS", "false") == "true" else subprocess.PIPE,
        stderr=None if os.environ.get("TEST_SHOW_SERVER_LOGS", "false") == "true" else subprocess.PIPE,
        preexec_fn=os.setsid
    )


def write_backend_coverage(cov):
    backendcov = coverage.data.CoverageData()
    with open('.coverage.backend') as fp:
        backendcov.read_fileobj(fp)
    cov.data.update(backendcov)


def setup_mock_kafka_connect_api(mock_name):
    kafka_connect_port = mocks.get_free_port()
    mocks.start_mock_server(kafka_connect_port, mock_name)
    return kafka_connect_port


def wait_for_servers_to_be_up(kafka_connect_url):
    is_alive = False
    while is_alive is False:
        is_alive = are_servers_up("http://localhost:18083", kafka_connect_url)
        time.sleep(0.2)


def are_servers_up(healthcheck_url, kafka_connect_url):
    try:
        if kafka_connect_url is not None:
            response = requests.head(healthcheck_url)
            is_mock_server_alive = response.status_code == 200
        else:
            is_mock_server_alive = True
        response = requests.head(healthcheck_url)
        return response.status_code == 200 and is_mock_server_alive
    except ConnectionError:
        return False


def is_coverage_on(request):
    return len(request.config.getoption('--cov')) != 0
