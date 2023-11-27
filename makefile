include common.mk

API_DIR = server
DB_DIR = db
REQ_DIR = .

FORCE:

prod: tests github

github: FORCE
	- git commit -a
	git push origin master

all_tests: db server

server: FORCE
	export CLOUD_MONGO=0; cd $(API_DIR); make tests;

db: FORCE
	export CLOUD_MONGO=0; cd $(DB_DIR); make tests;

dev_env: FORCE
	pip install -r $(REQ_DIR)/requirements-dev.txt

docs: FORCE
	cd $(API_DIR); make docs
