PYTHON = python

PROJECT = damn
DOCS_DIR = docs

.PHONY: build install distribute docs develop test test-all lint clean help

all: build install docs

build: $(SOURCES)
	$(PYTHON) setup.py build

install: 
	$(PYTHON) setup.py install

distribute:
	$(PYTHON) setup.py sdist

docs:
	@sphinx-apidoc -F -o $(DOCS_DIR) $(PROJECT)
	@sphinx-build -b html $(DOCS_DIR) $(DOCS_DIR)/_build/html

develop:
	$(PYTHON) setup.py develop

test:
	py.test -v --cov=$(PROJECT) --cov-report term tests

test-all:
	$(PYTHON) setup.py test

lint:
	pep8 --show-source --statistics --count $(PROJECT)

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
	@echo "  lint       : run PEP8 lint checking"
	@echo "  clean      : remove all build files"

