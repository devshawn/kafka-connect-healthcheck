# kafka-connect-healthcheck

![Python CI](https://github.com/devshawn/kafka-connect-healthcheck/workflows/Python%20CI/badge.svg) [![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/devshawn/kafka-connect-healthcheck.svg)](https://hub.docker.com/r/devshawn/kafka-connect-healthcheck) ![PyPI](https://img.shields.io/pypi/v/kafka-connect-healthcheck.svg?color=blue) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/kafka-connect-healthcheck.svg) [![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)


A simple healthcheck wrapper to monitor Kafka Connect.


<p align="center">
    <img src="https://i.imgur.com/veSZDFf.png"/>
</p>

Kafka Connect Healthcheck is a server that wraps the Kafka Connect API and provides a singular API endpoint to determine the health of a Kafka Connect instance. This can be used to alert or take action on unhealthy connectors and tasks. 

This can be used in numerous ways. It can sit as a standalone service for monitoring purposes, it can be used as a sidecar container to mark Kafka Connect workers as unhealthy in Kubernetes, or it can be used to provide logs of when connectors/tasks failed and reasons for their failures.

By default, the root endpoint `/` will return `200 OK` healthy if all connectors and tasks are in a state other than `FAILED`. It will return `503 Service Unavailable` if any connector or tasks are in a `FAILED` state.

## Usage

Kafka Connect Healthcheck can be installed as a command-line tool through `pip` or it can be used as a standalone Docker container. It could also be installed as a part of a custom Kafka Connect docker image.

### Command-Line
To use `kafka-connect-healthcheck` from the command-line, you must have `python` and `pip` installed. Currently, only Python 3 is supported.

You can install `kafka-connect-healthcheck` via pip:

```bash
pip install kafka-connect-healthcheck
```

To start the healthcheck server, run:

```bash
kafka-connect-healthcheck
```

The server will now be running on [localhost:18083][localhost].

### Docker
The `kafka-connect-healthcheck` image can be found on Docker Hub. 

You can pull down the latest image by running:

```bash
docker pull devshawn/kafka-connect-healthcheck
```

To start the healthcheck server, run:

```bash
docker run --rm -it -p 18083:18083 devshawn/kafka-connect-healthcheck
```

The server will now be running on [localhost:18083][localhost].

## Configuration
Kafka Connect Healthcheck can be configured via command-line arguments or by environment variables. 

#### Port
The port for the `kafka-connect-healthcheck` API.

| Usage                 | Value              |
|-----------------------|--------------------|
| Environment Variable  | `HEALTHCHECK_PORT` |
| Command-Line Argument | `--port`           |
| Default Value         | `18083`            |

#### Connect URL
The full URL of the Kafka Connect REST API. This is used to determine the health of the connect instance.

| Usage                 | Value                     |
|-----------------------|---------------------------|
| Environment Variable  | `HEALTHCHECK_CONNECT_URL` |
| Command-Line Argument | `--connect-url`           |
| Default Value         | `http://localhost:8083`   |

#### Connect Worker ID
The worker ID to monitor (usually the IP address of the connect worker). If none is set, all workers will be monitored and any failure will result in an unhealthy response.

| Usage                 | Value                           |
|-----------------------|---------------------------------|
| Environment Variable  | `HEALTHCHECK_CONNECT_WORKER_ID` |
| Command-Line Argument | `--connect-worker-id`           |
| Default Value         | None (all workers monitored)    |

**Note**: It is highly recommended to run an instance of the healthcheck for each worker if you're planning to restart containers based on the health.

#### Unhealthy States
A comma-separated list of connector and tasks states to be marked as unhealthy. 

| Usage                 | Value                                       |
|-----------------------|---------------------------------------------|
| Environment Variable  | `HEALTHCHECK_UNHEALTHY_STATES`              |
| Command-Line Argument | `--unhealthy-states`                        |
| Default Value         | `FAILED`                                    |
| Valid Values          | `FAILED`, `PAUSED`, `UNASSIGNED`, `RUNNING` |

**Note**: It's recommended to keep this defaulted to `FAILED`, but paused connectors or tasks can be marked as unhealthy by passing `FAILED,PAUSED`. 

#### Log Level
The level of logs to be shown by the application.

| Usage                 | Value                                       |
|-----------------------|---------------------------------------------|
| Environment Variable  | `HEALTHCHECK_LOG_LEVEL`                     |
| Command-Line Argument | `--log-level`                               |
| Default Value         | `INFO`                                      |
| Valid Values          | `DEBUG`, `INFO`, `WARNING`, `ERROR`         |

All healthy connector and task statuses are logged at `INFO`. Unhealthy ones are logged at `WARNING`. Any communication or HTTP errors are logged at `ERROR`.

## API
The server provides a very simple HTTP API which can be used for liveness probes and monitoring alerts. We expose two endpoints:

#### `GET /`
Get the current health status of the Kafka Connect system. This could be used as a sidecar to determine the health of each Kafka Connect worker and their associated connectors and tasks.

**Example Request**
```bash
curl http://localhost:18083
```

**Example Healthy Response**

200 OK
```json
{
    "failures": [],
    "failure_states": [
        "FAILED"
    ],
    "healthy": true
}
```

**Example Unhealthy Response**

503 Service Unavailable
```json
{
    "failures": [
        {
            "type": "connector",
            "connector": "jdbc-source",
            "state": "FAILED",
            "worker_id": "127.0.0.1:8083"
        },
        {
            "type": "task",
            "connector": "jdbc-source",
            "id": 0,
            "state": "FAILED",
            "worker_id": "127.0.0.1:8083",
            "trace": "..."
        }
    ],
    "failure_states": [
        "FAILED"
    ],
    "healthy": false
}
```

#### `GET /ping`
Get the current health status of the healthcheck server. This will always be successful as long as the server is still able to serve requests. This can be used as a ready or liveness probe in Kubernetes.

**Example Request**
```bash
curl http://localhost:18083/ping
```

**Example Response**

200 OK
```json
{
    "status": "UP"
}
```

## License
Copyright (c) 2019 Shawn Seymour.

Licensed under the [Apache 2.0 license][license].

[localhost]: http://localhost:18083
[license]: LICENSE
