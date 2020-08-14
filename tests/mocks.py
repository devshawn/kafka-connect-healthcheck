import os
import socket
from functools import partial
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread


# Mocks Kafka Connect REST API responses for integration tests
class MockServerRequestHandler(BaseHTTPRequestHandler):

    def __init__(self, mock_name, *args, **kwargs):
        self.mock_name = mock_name
        super().__init__(*args, **kwargs)

    def do_GET(self):
        status_code = 503 if "unhealthy" in self.mock_name else 200
        try:
            if self.path == "/connectors":
                with open(os.path.join(os.getcwd(), "tests/data/mocks/{}-connectors.json".format(self.mock_name)), "r") as f:
                    self.response(200, payload=f.read())
            else:
                split_path = self.path.split("/")
                if len(split_path) >= 4 and split_path[3] == "status":
                    connector_name = split_path[2]
                    path = os.path.join(os.getcwd(), "./tests/data/mocks/{}-connector-{}.json".format(self.mock_name, connector_name))
                    with open(path, "r") as f:
                        self.response(status_code, payload=f.read())
                else:
                    connector_name = split_path[2]
                    details_status_code = 503 if "unhealthy-broker" in self.mock_name else 200
                    path = os.path.join(os.getcwd(),
                                        "./tests/data/mocks/healthy-connector-details.json".format(self.mock_name, connector_name))
                    with open(path, "r") as f:
                        self.response(details_status_code, payload=f.read())

        except Exception as ex:
            print("Error while handling mock GET request: {}".format(ex))
            self.response(500, "")

    def response(self, status_code, payload):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(payload.encode('utf-8'))

    def log_message(self, format, *args):
        return


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


def start_mock_server(port, mock_name):
    handler = partial(MockServerRequestHandler, mock_name)
    mock_server = HTTPServer(('localhost', port), handler)
    mock_server_thread = Thread(target=mock_server.serve_forever)
    mock_server_thread.setDaemon(True)
    mock_server_thread.start()
    print("\nMock Kafka Connect server running on port: {}".format(port))
