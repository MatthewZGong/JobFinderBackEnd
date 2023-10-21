LINTER = flake8
API_DIR = server
DB_DIR = db
REQ_DIR = .

PYTESTFLAGS = -vv --verbose --cov-branch --cov-report term-missing --tb=short -W ignore::FutureWarning

FORCE:

docs: $(DOCFILES)

%.html: %.py
	pydoc3 -w ./$<
	git add $@

tests: lint

unit: FORCE
	pytest $(PYTESTFLAGS)

lint: FORCE
	$(LINTER) ./*.py
	$(LINTER) ./*.py