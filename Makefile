PYTHON = python

PROJECT = yodel
DOCS_DIR = docs
TEST_DIR = test

.PHONY: build install dist docs-generate docs develop test test-all lint readme-rst pypi-register pypi-upload clean help

all: build install docs

build: $(SOURCES)
	$(PYTHON) setup.py build

install: 
	$(PYTHON) setup.py install

dist:
	$(PYTHON) setup.py sdist

docs-generate:
	@sphinx-apidoc -F -e -o $(DOCS_DIR) $(PROJECT)
	@sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html

docs:
	@sphinx-apidoc -f -e -o $(DOCS_DIR) $(PROJECT)
	@sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html

develop:
	$(PYTHON) setup.py develop

test:
	py.test -v --cov=$(PROJECT) --cov-report term-missing $(TEST_DIR)

test-all:
	$(PYTHON) setup.py test

lint:
	pep8 --statistics --count --show-source $(PROJECT)

readme-rst:
	pandoc --from=markdown --to=rst README.md -o README.rst

pypi-register:
	$(PYTHON) setup.py register

pypi-upload:
	$(PYTHON) setup.py sdist upload

clean:
	@rm -rf build dist $(DOCS_DIR)/_build $(DOCS_DIR)/_static $(DOCS_DIR)/_templates $(PROJECT)/__pycache__ $(PROJECT)/*.pyc $(PROJECT).egg-info

help:
	@echo "  build         : build module"
	@echo "  install       : install module"
	@echo "  dist          : create source distribution archive"
	@echo "  docs-generate : generate documentation from scratch (no existing index)"
	@echo "  docs          : create documentation"
	@echo "  develop       : install module in development mode"
	@echo "  test          : run unit tests"
	@echo "  test-all      : run the whole testing suite"
	@echo "  lint          : run the PEP8 lint checker"
	@echo "  readme-rst    : generate README.rst based on README.md"
	@echo "  pypi-register : register current package version on PyPI"
	@echo "  pypi-upload   : upload current package version on PyPI"
	@echo "  clean         : remove all build files"

