.PHONY: install test run lint format

install:
`tpython -m pip install -r requirements.txt

run:
`tuvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000

test:
`tpython -m pytest

lint:
`truff check backend/src backend/integration

format:
`truff format backend/src backend/integration
