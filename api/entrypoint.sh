#!/bin/bash
pip3 install -r /opt/BC3/api/requirements.txt

flask --app main run --host=0.0.0.0 --port=5002 --debug
