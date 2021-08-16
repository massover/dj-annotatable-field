test:
	poetry run pytest

lint:
	poetry run isort .
	poetry run black .

cov: ## check code coverage quickly
	poetry run pytest --cov=. --cov-branch -v --durations=25
	poetry run coverage report -m
	poetry run coverage html
	open htmlcov/index.html

