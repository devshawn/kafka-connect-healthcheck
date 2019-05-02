#!/usr/bin/env bash

flake8 --max-line-length=135 --inline-quotes '"' --exclude=.tox,htmlcov,build,tests,scratch,docs,venv .
