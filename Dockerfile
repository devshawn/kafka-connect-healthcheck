FROM python:3.7-alpine

COPY setup.py README.md LICENSE /kafka-connect-healthcheck/
COPY kafka_connect_healthcheck/ /kafka-connect-healthcheck/kafka_connect_healthcheck/

RUN cd /kafka-connect-healthcheck && pip3 install -e .

CMD ["kafka-connect-healthcheck"]
