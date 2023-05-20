.PHYONY = help run setup dev-setup test format clean lint coverage

port := 8000

help:
	@echo "------------------HELP------------------"
	@echo "help      - get this help message"
	@echo "setup     - setup project"
	@echo "dev-setup - setup project for development"
	@echo "clean     - remove Python artifacts"
	@echo "coverage  - measure code coverage"
	@echo "format    - format code with black"
	@echo "lint      - check style with flake8"
	@echo "test      - run tests with pytest"
	@echo "-----------------------------------------"

setup:
	@echo "Setting up project..."
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt
	python -m pip install -e .

dev-setup:
	@echo "Setting up project for development..."
	python -m pip install -r requirements-dev.txt

test:
	python -m pytest -c pytest.ini

format:
	python -m black .

lint:
	python -m flake8 . --config flake8.ini

coverage:
	coverage run -m pytest -c pytest.ini
	coverage report
	coverage html

clean:
	rm -rf `find . -name __pycache__  -type d`
	find . -name '*~' -exec rm -iv {} +
