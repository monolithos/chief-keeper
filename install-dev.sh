#!/usr/bin/env bash

cd "$(dirname "$0")"
set -e

rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# The advantage of using this method, in contrary to just calling `pip3 install -r requirements.txt` several times,
# is that it can detect different versions of the same dependency and fail with a "Double requirement given"
# error message.
#pip install $(cat requirements.txt $(find lib -name requirements.txt | sort) | sort | uniq | sed 's/ *== */==/g')
#pip install $(cat requirements-dev.txt $(find lib -name requirements-dev.txt | sort) | sort | uniq | sed 's/ *== */==/g')

pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
