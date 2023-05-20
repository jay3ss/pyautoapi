.PHYONY = help run setup

port := 8000

help:
	@echo "---------------HELP-----------------"
	@echo "To setup the project type make setup"
	@echo "To clean the project type make clean"
	@echo "To run the project type make run"
	@echo "------------------------------------"

setup:
	@echo "Setting up project..."
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	python -m pip install -e .

dev-setup:
	@echo "Setting up project for development..."
	python -m pip install -r requirements-dev.txt

test:
	python tests/bin/create_test_database.py
	python -m pytest -vv
	rm tests/data/test.db

static-analysis:
	python -m black .
	python -m flake8 .

clean:
	rm -rf `find . -name __pycache__  -type d`

