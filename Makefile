PIPENV := pipenv
PYTHON := $(PIPENV) run python
PACKAGE := your_package_name

.DEFAULT_GOAL := help

help:
	@echo "Targets:"
	@echo "  make sdist      Build source distribution"
	@echo "  make wheel      Build wheel only"
	@echo "  make build      Build sdist + wheel"
	@echo "  make clean      Remove build artifacts"
	@echo "  make uninstall  Uninstall package"

clean:
	rm -rf build dist *.egg-info __pycache__ .pytest_cache

uninstall:
	$(PIPENV) run pip uninstall -y $(PACKAGE) || true

sdist:
	$(PYTHON) -m build --sdist

wheel:
	$(PYTHON) -m build --wheel

build:
	$(PYTHON) -m build
