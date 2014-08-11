PYTHON = python

PROJECT = yodel
DOCS_DIR = docs
TEST_DIR = tests

.PHONY: build install distribute docs develop test test-all lint clean help

all: build install docs

build: $(SOURCES)
	$(PYTHON) setup.py build

install: 
	$(PYTHON) setup.py install

distribute:
	$(PYTHON) setup.py sdist

docs:
	@sphinx-apidoc -F -e -o $(DOCS_DIR) $(PROJECT)
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

clean:
	@rm -rf build dist $(DOCS_DIR)/_build $(PROJECT)/__pycache__ $(PROJECT)/*.pyc

help:
	@echo "  build      : build module"
	@echo "  install    : install module"
	@echo "  distribute : create source distribution archive"
	@echo "  docs       : create documentation"
	@echo "  develop    : install module in development mode"
	@echo "  test       : run unit tests"
	@echo "  test-all   : run the whole testing suite"
	@echo "  lint       : run the PEP8 lint checker"
	@echo "  clean      : remove all build files"

