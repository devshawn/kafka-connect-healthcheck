# tests/test_server.py

import json

import pytest
import requests

scenario_0 = ({}, "0-healthcheck-server-healthy")
scenario_1 = ({"HEALTHCHECK_UNHEALTHY_STATES": "FAILED"}, "1-healthy")
scenario_2 = ({"HEALTHCHECK_UNHEALTHY_STATES": "FAILED"}, "2-unhealthy")
scenario_3 = ({"HEALTHCHECK_CONNECT_URL": "http://unknown-hostname:8083"}, "3-unhealthy-error")
scenario_4 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "kafka-connect:8083"}, "4-healthy-worker-id-correct")
scenario_5 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "kafka-connect:8083"}, "5-healthy-worker-id-unused")
scenario_6 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "kafka-connect:8083"}, "6-healthy-worker-id-with-other-workers-failing")
scenario_7 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "kafka-connect:8083"}, "7-unhealthy-worker-id-with-other-workers-healthy")
scenario_8 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "my.worker.name:8083"}, "8-healthy-multiple-tasks")
scenario_9 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "my.worker.name:8083"}, "9-healthy-multiple-connectors")
scenario_10 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "my.worker.name:8083"}, "10-unhealthy-multiple-connectors")
scenario_11 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "my.worker.name:8083"}, "11-healthy-no-connectors")
scenario_12 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "my.worker.name:8083"}, "12-unhealthy-task-with-trace")
scenario_13 = ({"HEALTHCHECK_CONNECT_WORKER_ID": "unhealthy.worker:8083"}, "13-unhealthy-broker-connection")
other_scenarios = ({}, None)


@pytest.mark.parametrize("run_backend", [scenario_0], indirect=True)
def test_0_healthcheck_server_healthy(run_backend):
    with open("tests/data/expected/0-healthcheck-server-healthy.json", "r") as f:
        response = requests.get("http://localhost:18083/ping")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_1], indirect=True)
def test_1_healthy(run_backend, request):
    with open("tests/data/expected/1-healthy.json", "r") as f:
        response = requests.get("http://localhost:18083")
        logs = request.config.cache.get("logs", "") == ""
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_2], indirect=True)
def test_2_unhealthy(run_backend):
    with open("tests/data/expected/2-unhealthy.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 503
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_3], indirect=True)
def test_3_unhealthy_error(run_backend):
    with open("tests/data/expected/3-unhealthy-error.json", "r") as f:
        response = requests.get("http://localhost:18083/")
        expected_response = json.load(f)
        actual_response = json.loads(response.content.decode("utf-8"))
        assert response.status_code == 503
        assert actual_response["healthy"] == expected_response["healthy"]
        assert actual_response["message"] == expected_response["message"]
        assert actual_response["failure_states"] == expected_response["failure_states"]
        assert expected_response["error"] in actual_response["error"]


@pytest.mark.parametrize("run_backend", [scenario_4], indirect=True)
def test_4_healthy_worker_id_correct(run_backend):
    with open("tests/data/expected/4-healthy-worker-id-correct.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_5], indirect=True)
def test_5_healthy_worker_id_unused(run_backend):
    with open("tests/data/expected/5-healthy-worker-id-unused.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_6], indirect=True)
def test_6_healthy_worker_id_with_other_workers_failing(run_backend):
    with open("tests/data/expected/6-healthy-worker-id-with-other-workers-failing.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_7], indirect=True)
def test_7_unhealthy_worker_id_with_other_workers_healthy(run_backend):
    with open("tests/data/expected/7-unhealthy-worker-id-with-other-workers-healthy.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 503
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_8], indirect=True)
def test_8_healthy_multiple_tasks(run_backend):
    with open("tests/data/expected/8-healthy-multiple-tasks.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_9], indirect=True)
def test_9_healthy_multiple_connectors(run_backend):
    with open("tests/data/expected/9-healthy-multiple-connectors.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_10], indirect=True)
def test_10_unhealthy_multiple_connectors(run_backend):
    with open("tests/data/expected/10-unhealthy-multiple-connectors.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 503
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_11], indirect=True)
def test_11_healthy_no_connectors(run_backend):
    with open("tests/data/expected/11-healthy-no-connectors.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 200
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_12], indirect=True)
def test_12_unhealthy_task_with_trace(run_backend):
    with open("tests/data/expected/12-unhealthy-task-with-trace.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 503
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("run_backend", [scenario_13], indirect=True)
def test_13_unhealthy_broker_connection(run_backend):
    with open("tests/data/expected/13-unhealthy-broker-connection.json", "r") as f:
        response = requests.get("http://localhost:18083")
        assert response.status_code == 503
        assert json.loads(response.content.decode("utf-8")) == json.load(f)


@pytest.mark.parametrize("test_input", ["test", "does/not/exist", "kafka", "this-is-a-long/url", "connectors"])
@pytest.mark.parametrize("run_backend", [other_scenarios], indirect=True)
def test_for_404s(run_backend, test_input):
    response = requests.get("http://localhost:18083/{}".format(test_input))
    assert response.status_code == 404
    assert response.content == b""


@pytest.mark.parametrize("test_input", ["", "test", "does/not/exist"])
@pytest.mark.parametrize("run_backend", [other_scenarios], indirect=True)
def test_head_request(run_backend, test_input):
    response = requests.head("http://localhost:18083/{}".format(test_input))
    assert response.status_code == 200
    assert response.headers.get("Content-type") == "text/html"
    assert response.content == b""
