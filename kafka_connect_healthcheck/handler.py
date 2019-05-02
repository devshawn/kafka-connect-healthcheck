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

import json

from http.server import BaseHTTPRequestHandler


class RequestHandler(BaseHTTPRequestHandler):

    def __init__(self, health, *args, **kwargs):
        self.health = health
        super().__init__(*args, **kwargs)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        if self.path in ["/"]:
            payload = self.health.get_health_result()
            payload_json = json.dumps(payload)
            status = 200 if payload["healthy"] else 503
            self.respond(status, payload_json)
        elif self.path in ["/ping"]:
            payload_json = json.dumps({"status": "UP"})
            self.respond(200, payload_json)
        else:
            self.respond(404, "")

    def log_message(self, format, *args):
        return

    def handle_http(self, status_code, payload):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        return bytes(payload, "UTF-8")

    def respond(self, status, payload):
        response = self.handle_http(status, payload)
        self.wfile.write(response)
