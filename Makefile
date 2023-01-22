.PHONY: test
test: lint
	python -m unittest tests.units.test_synopkg

.PHONY: fmt
fmt:
	black library/

.PHONY: lint
lint:
	mypy library/
