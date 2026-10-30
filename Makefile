SHELL = /bin/bash -o pipefail

.PHONY: help install install-poetry lock build publish-pypi check-version lint format lint-fix typecheck \
	check-architecture check-spec test test-unit test-features test-network check-quality check-all \
	generate-tests-from-features install-antora build-docs clean-docs serve-docs preview-docs

include .env-dev

BUILD_PRINT = \e[1;34mSTEP: \e[0m
END_BUILD_PRINT = \e[0m

PACKAGE_NAME = eds4jinja2
TEST_PATH = tests
OPENSPEC = npx -y @fission-ai/openspec@1.4.1
# Coverage is reported, not gated (modernize-library-py312 DEC-10).
COV_FLAGS = --cov=$(PACKAGE_NAME) --cov-report=term --cov-report=xml:coverage.xml

.DEFAULT_GOAL := help

help: ## Display available targets
	@ grep -hE '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-26s\033[0m %s\n", $$1, $$2}'

#-----------------------------------------------------------------------------
# Install / build
#-----------------------------------------------------------------------------

install-poetry: ## Install Poetry if not present
	@ command -v poetry >/dev/null || python -m pip install "poetry>=2.0.0,<3.0.0"

install: install-poetry ## Install the package with all dependency groups
	@ echo -e "$(BUILD_PRINT)Installing dependencies$(END_BUILD_PRINT)"
	@ poetry install --with test,lint,dev --all-extras

lock: ## Update poetry.lock
	@ poetry lock

build: check-version ## Build the sdist and wheel into dist/
	@ echo -e "$(BUILD_PRINT)Building the distribution$(END_BUILD_PRINT)"
	@ rm -rf dist
	@ poetry build

publish-pypi: build ## Check and upload dist/ to PyPI (CI uses Trusted Publishing instead)
	@ poetry run twine check dist/*
	@ poetry run twine upload --skip-existing dist/*

#-----------------------------------------------------------------------------
# Quality gates — `make check-all` is the gate CI runs
#-----------------------------------------------------------------------------

check-version: ## Fail when pyproject's version drifts from eds4jinja2/VERSION
	@ test "$$(poetry version -s)" = "$$(cat $(PACKAGE_NAME)/VERSION)" \
		|| (echo "pyproject version $$(poetry version -s) != VERSION $$(cat $(PACKAGE_NAME)/VERSION)" && exit 1)

lint: ## Ruff lint and format check
	@ echo -e "$(BUILD_PRINT)Ruff$(END_BUILD_PRINT)"
	@ poetry run ruff check $(PACKAGE_NAME) $(TEST_PATH)
	@ poetry run ruff format --check $(PACKAGE_NAME) $(TEST_PATH)

format: ## Format code with Ruff
	@ poetry run ruff format $(PACKAGE_NAME) $(TEST_PATH)

lint-fix: ## Ruff auto-fix
	@ poetry run ruff check --fix $(PACKAGE_NAME) $(TEST_PATH)

typecheck: ## mypy type check of the package
	@ echo -e "$(BUILD_PRINT)mypy$(END_BUILD_PRINT)"
	@ poetry run mypy $(PACKAGE_NAME)

check-architecture: ## Check layer boundaries (import-linter)
	@ echo -e "$(BUILD_PRINT)Checking layer boundaries (import-linter)$(END_BUILD_PRINT)"
	@ poetry run lint-imports --config .importlinter

check-spec: ## Validate the OpenSpec spine strictly (needs Node.js)
	@ echo -e "$(BUILD_PRINT)openspec validate --strict$(END_BUILD_PRINT)"
	@ $(OPENSPEC) validate --all --strict

test: ## All non-network tests, with coverage report
	@ echo -e "$(BUILD_PRINT)Running all tests (excludes live-network tests)$(END_BUILD_PRINT)"
	@ poetry run pytest $(TEST_PATH) -m "not network" $(COV_FLAGS) --junitxml=junit_report.xml

test-unit: ## Unit tests only
	@ poetry run pytest $(TEST_PATH)/unit -m "not network"

test-features: ## Gherkin feature tests only
	@ poetry run pytest $(TEST_PATH)/steps -m "not network"

test-network: ## Live-network integration tests (need network)
	@ poetry run pytest $(TEST_PATH) -m network

check-quality: check-version lint typecheck check-architecture check-spec ## Static checks
	@ echo -e "$(BUILD_PRINT)All quality checks passed$(END_BUILD_PRINT)"

check-all: check-quality test ## The full gate: static checks + tests
	@ echo -e "$(BUILD_PRINT)Full verification suite passed$(END_BUILD_PRINT)"

#-----------------------------------------------------------------------------
# Gherkin feature and acceptance test generation commands
#-----------------------------------------------------------------------------

FEATURES_FOLDER = tests/features
STEPS_FOLDER = tests/steps
FEATURE_FILES := $(wildcard $(FEATURES_FOLDER)/*.feature)
EXISTENT_TEST_FILES = $(wildcard $(STEPS_FOLDER)/*.py)
HYPOTHETICAL_TEST_FILES :=  $(addprefix $(STEPS_FOLDER)/test_, $(notdir $(FEATURE_FILES:.feature=.py)))
TEST_FILES := $(filter-out $(EXISTENT_TEST_FILES),$(HYPOTHETICAL_TEST_FILES))

generate-tests-from-features: $(TEST_FILES)
	@ echo "$(BUILD_PRINT)The following test files should be generated: $(TEST_FILES)"
	@ echo "$(BUILD_PRINT)Done generating missing feature files"
	@ echo "$(BUILD_PRINT)Verifying if there are any missing step implementations"
	@ poetry run pytest --generate-missing --feature $(FEATURES_FOLDER)

$(addprefix $(STEPS_FOLDER)/test_, $(notdir $(STEPS_FOLDER)/%.py)): $(FEATURES_FOLDER)/%.feature
	@ echo "$(BUILD_PRINT)Generating the testfile "$@"  from "$<" feature file"
	@ poetry run pytest-bdd generate $< > $@
	@ sed -i  's|features|../features|' $@

#-----------------------------------------------------------------------------
# Fuseki related commands
#-----------------------------------------------------------------------------

start-fuseki:
	@ echo "$(BUILD_PRINT)Starting Fuseki on port $(if $(FUSEKI_PORT),$(FUSEKI_PORT),'default port')"
	@ docker-compose --file docker-compose.yml --env-file .env-dev up -d fuseki

stop-fuseki:
	@ echo "$(BUILD_PRINT)Stopping Fuseki"
	@ docker-compose --file docker-compose.yml --env-file .env-dev down

fuseki-create-test-dbs:
	@ echo "$(BUILD_PRINT)Building dummy "subdiv" and "abc" datasets at http://localhost:$(if $(FUSEKI_PORT),$(FUSEKI_PORT),unknown port)/$$/datasets"
	@ sleep 2
	@ curl --anyauth --user 'admin:admin' -d 'dbType=mem&dbName=subdiv'  'http://localhost:$(FUSEKI_PORT)/$$/datasets'
	@ curl --anyauth --user 'admin:admin' -d 'dbType=mem&dbName=abc'  'http://localhost:$(FUSEKI_PORT)/$$/datasets'

clean-data:
	@ echo "$(BUILD_PRINT)Deleting the $(DATA_FOLDER)"
	@ sudo rm -rf $(DATA_FOLDER)

start-service: start-fuseki fuseki-create-test-dbs

stop-service: stop-fuseki clean-data


#-----------------------------------------------------------------------------
# Documentation (AsciiDoc + Antora, Node-based)
#-----------------------------------------------------------------------------

NODE ?= $(shell command -v node)
NPM ?= $(shell command -v npm)
DOC_BUILD_DIR = docs/build
ANTORA_PLAYBOOK = docs/antora-playbook.local.yml

check-node:
ifeq ($(NODE),)
	@ echo -e "$(BUILD_PRINT)Node.js is not installed. Install Node.js 18+ first." && exit 1
endif

install-antora: check-node
	@ echo -e "$(BUILD_PRINT)Installing Antora and extensions (npm)$(END_BUILD_PRINT)"
	@ npm install

build-docs: install-antora
	@ echo -e "$(BUILD_PRINT)Building the documentation site with Antora$(END_BUILD_PRINT)"
	@ npx antora --fetch $(ANTORA_PLAYBOOK)

clean-docs:
	@ echo -e "$(BUILD_PRINT)Cleaning the Antora build$(END_BUILD_PRINT)"
	@ rm -rf $(DOC_BUILD_DIR)

serve-docs:
	@ echo -e "$(BUILD_PRINT)Serving docs at http://localhost:8088$(END_BUILD_PRINT)"
	@ python3 -m http.server 8088 --directory $(DOC_BUILD_DIR)/site

preview-docs: build-docs serve-docs

