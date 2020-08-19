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

import logging

import requests

from kafka_connect_healthcheck import helpers


class Health:

    def __init__(self, connect_url, worker_id, unhealthy_states, auth):
        self.connect_url = connect_url
        self.worker_id = worker_id
        self.unhealthy_states = [x.upper().strip() for x in unhealthy_states]
        self.kwargs = {}
        if auth and ":" in auth:
            self.kwargs["auth"] = tuple(auth.split(":"))
            self.log_initialization_values()

    def get_health_result(self):
        try:
            health_result = {"failures": [], "failure_states": self.unhealthy_states}
            connector_names = self.get_connector_names()
            connector_statuses = self.get_connectors_health(connector_names)
            self.handle_healthcheck(connector_statuses, health_result)
            health_result["healthy"] = len(health_result["failures"]) == 0
        except Exception as ex:
            logging.error("Error while attempting to calculate health result. Assuming unhealthy. Error: {}".format(ex))
            logging.error(ex)
            health_result = {
                "healthy": False,
                "message": "Exception raised while attempting to calculate health result, assuming unhealthy.",
                "error": "{}".format(ex),
                "failure_states": self.unhealthy_states
            }
        helpers.log_line_break()
        return health_result

    def handle_healthcheck(self, connector_statuses, health_result):
        connectors_on_this_worker = False
        for connector in connector_statuses:
            if self.is_on_this_worker(connector["worker_id"]):
                connectors_on_this_worker = True
                if self.is_in_unhealthy_state(connector["state"]):
                    logging.warning("Connector '{}' is unhealthy in failure state: {}".format(connector["name"], connector["state"]))
                    health_result["failures"].append({
                        "type": "connector",
                        "connector": connector["name"],
                        "state": connector["state"],
                        "worker_id": connector["worker_id"]
                    })
                else:
                    logging.info("Connector '{}' is healthy in state: {}".format(connector["name"], connector["state"]))
            self.handle_task_healthcheck(connector, health_result)
        if not connectors_on_this_worker and connector_statuses:
            self.handle_broker_healthcheck(health_result, connector_statuses[0]["name"])

    def handle_broker_healthcheck(self, health_result, connector_name):
        try:
            self.get_connector_details(connector_name)
        except Exception as ex:
            logging.error("Error while attempting to get details for {}. Assuming unhealthy. Error: {}".format(connector_name, ex))
            logging.error(ex)
            health_result["failures"].append({
                "type": "broker",
                "connector": connector_name,
            })

    def handle_task_healthcheck(self, connector, health_result):
        for task in connector["tasks"]:
            if self.is_on_this_worker(task["worker_id"]):
                if self.is_in_unhealthy_state(task["state"]):
                    logging.warning("Connector '{}' task '{}' is unhealthy in failure state: {}".format(
                        connector["name"], task["id"], task["state"]
                    ))
                    health_result["failures"].append({
                        "type": "task",
                        "connector": connector["name"],
                        "id": task["id"],
                        "state": task["state"],
                        "worker_id": task["worker_id"],
                        "trace": task.get("trace", None)
                    })
                else:
                    logging.info("Connector '{}' task '{}' is healthy in state: {}".format(
                        connector["name"], task["id"], task["state"]
                    ))

    def get_connectors_health(self, connector_names):
        statuses = []
        for connector_name in connector_names:
            statuses.append(self.get_connector_health(connector_name))
        return statuses

    def get_connector_health(self, connector_name):
        connector_status = self.get_connector_status(connector_name)
        connector_state = connector_status["connector"]["state"].upper()
        connector_worker = connector_status["connector"]["worker_id"]
        return {
            "name": connector_name,
            "state": connector_state,
            "worker_id": connector_worker,
            "tasks": connector_status["tasks"]
        }

    def get_connector_names(self):
        response = requests.get("{}/connectors".format(self.connect_url), **self.kwargs)
        response_json = response.json()
        return response_json

    def get_connector_status(self, connector_name):
        response = requests.get("{}/connectors/{}/status".format(self.connect_url, connector_name), **self.kwargs)
        response_json = response.json()
        return response_json

    def get_connector_details(self, connector_name):
        response = requests.get("{}/connectors/{}".format(self.connect_url, connector_name), **self.kwargs)
        response.raise_for_status()
        response_json = response.json()
        return response_json

    def is_in_unhealthy_state(self, state):
        return state.upper() in self.unhealthy_states

    def is_on_this_worker(self, response_worker_id):
        return response_worker_id.lower() == self.worker_id.lower() if self.worker_id is not None else True

    def log_initialization_values(self):
        logging.info("Server will report unhealthy for states: '{}'".format(", ".join(self.unhealthy_states)))
        logging.info("Server will healthcheck against Kafka Connect at: {}".format(self.connect_url))
        if "auth" in self.kwargs:
            logging.info("Server will use basic authentication against Kafka Connect")
        if self.worker_id is not None:
            logging.info("Server will healthcheck connectors and tasks for worker with id '{}'".format(self.worker_id))
        else:
            logging.warning("No worker id supplied, server will healthcheck all connectors and tasks")
