#!/bin/bash

set -e

sed -i "" -e "s#boto3.*##g" requirements.txt
sed -i "" -e "s#black.*##g" requirements.txt
sed -i "" -e "s#pytype.*##g" requirements.txt
test -d source || mkdir -p source
pip install --target ./source -r requirements.txt
cp -p lambda_function.py ./source/lambda_function.py
git co requirements.txt
