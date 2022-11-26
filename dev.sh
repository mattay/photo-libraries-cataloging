SRC=src
echo "mypy"
pipenv run mypy ${SRC}

echo "flake8"
pipenv run flake8 ${SRC}

echo "pytest"
pipenv run pytest