import setuptools

meta = {}

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("kafka_connect_healthcheck/version.py") as f:
    exec(f.read(), meta)

requires = [
    "requests>=2.21.0"
]

setuptools.setup(
    name="kafka-connect-healthcheck",
    version=meta["__version__"],
    author="Shawn Seymour",
    author_email="shawn@devshawn.com",
    description="A simple healthcheck wrapper to monitor Kafka Connect.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/devshawn/kafka-connect-healthcheck",
    license="Apache License 2.0",
    packages=["kafka_connect_healthcheck"],
    install_requires=requires,
    entry_points={
        "console_scripts": ["kafka-connect-healthcheck=kafka_connect_healthcheck.main:main"],
    },
    keywords=("kafka", "connect", "health", "healthcheck", "wrapper", "monitor", "connector"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
