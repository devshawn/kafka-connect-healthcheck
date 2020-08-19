#  -*- coding: utf-8 -*-
#
#  Copyright 2019 Shawn Seymour. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License"). You
#  may not use this file except in compliance with the License. A copy of
#  the License is located at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  or in the "license" file accompanying this file. This file is
#  distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
#  ANY KIND, either express or implied. See the License for the specific
#  language governing permissions and limitations under the License.

import argparse
import os


def get_parser():
    parser = argparse.ArgumentParser(description="A simple healthcheck for Kafka Connect. It can wrap a Kafka Connect "
                                                 "process so you can check the health of specific connectors. "
                                                 "This can be used as a health check within Kubernetes to automatically "
                                                 "restart failed connect instances.")

    parser.add_argument("--port",
                        default=os.environ.get("HEALTHCHECK_PORT", "18083"),
                        dest="healthcheck_port",
                        type=int,
                        nargs="?",
                        help="The port for the healthcheck HTTP server."
                        )

    parser.add_argument("--connect-url",
                        default=os.environ.get("HEALTHCHECK_CONNECT_URL", "http://localhost:8083"),
                        dest="connect_url",
                        nargs="?",
                        help="The Kafka Connect REST API URL that the health check will be run against."
                        )

    parser.add_argument("--connect-worker-id",
                        default=os.environ.get("HEALTHCHECK_CONNECT_WORKER_ID"),
                        dest="connect_worker_id",
                        nargs="?",
                        help="The Kafka Connect REST API URL that the health check will be run against."
                        )

    parser.add_argument("--unhealthy-states",
                        default=os.environ.get("HEALTHCHECK_UNHEALTHY_STATES", "FAILED").upper(),
                        dest="unhealthy_states",
                        nargs="?",
                        help="A comma separated lists of connector and task states to be marked as unhealthy. Default: FAILED."
                        )

    parser.add_argument("--basic-auth",
                        default=os.environ.get("HEALTHCHECK_BASIC_AUTH", ""),
                        dest="basic_auth",
                        nargs="?",
                        help="Colon-separated credentials for basic HTTP authentication. Default: empty.")

    parser.add_argument("--log-level",
                        default=os.environ.get("HEALTHCHECK_LOG_LEVEL", "INFO").upper(),
                        dest="log_level",
                        nargs="?",
                        help="The level of logs to be shown. Default: INFO.")

    return parser
