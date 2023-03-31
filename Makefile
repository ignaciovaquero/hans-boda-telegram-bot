.PHONY: venv requirements lint test build init deploy clean

venv:
	test -d venv || python3.10 -m venv venv
	. venv/bin/activate

requirements: venv
	venv/bin/pip install -r requirements.txt -r tests/requirements.txt

lint: requirements
	venv/bin/black *.py tests/*.py

type: requirements
	venv/bin/pytype *.py tests/*.py

test: lint
	venv/bin/pytest --cov . tests/

build: lint type
	./build_lambda.sh

init:
	terraform -chdir=terraform init

deploy: build init
	terraform -chdir=terraform apply -auto-approve
	rm -rf venv source terraform/builds

clean:
	rm -rf venv source terraform/builds
