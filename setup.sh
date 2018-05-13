#!/bin/bash

sudo apt install -y python3-pip

pip3 install virtualenv

virtualenv venv

pip3 install -r requirements.txt

source venv/bin/activate

pip3 install -r requirements.txt

export FLASK_APP=diffaltimetry.py

python3 db_create.py

flask run


