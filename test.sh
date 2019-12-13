#!/bin/bash
python purge.py
rm coverage_report.txt

PYTHONPATH='.' coverage run tests/twitch_application_test.py
echo ----All---- >>  coverage_report.txt
coverage report -m >> coverage_report.txt
python purge.py
