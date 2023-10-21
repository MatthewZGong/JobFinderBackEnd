LINTER = flake8
API_DIR = server
DB_DIR = db
REQ_DIR = .

PKG = $(API_DIR)
PYTESTFLAGS = -vv --verbose --cov-branch --cov-report term-missing --tb=short -W ignore::FutureWarning

FORCE:

prod: tests github

github: FORCE
	- git commit -a
	git push origin master

tests: db server

server: FORCE
	cd $(API_DIR); make tests;

db: FORCE
	cd $(DB_DIR); make tests;

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt

docs: FORCE
	cd $(API_DIR); make docs
