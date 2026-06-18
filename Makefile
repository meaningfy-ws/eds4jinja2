.PHONY: test install install-all install-dev build publish-pipy test-unit test-features test-all test-network generate-tests-from-features

include .env-dev

BUILD_PRINT = \e[1;34mSTEP: \e[0m

#-----------------------------------------------------------------------------
# Basic commands
#-----------------------------------------------------------------------------

install-all:
	@ echo -e "$(BUILD_PRINT)Installing the package with its dev extra$(END_BUILD_PRINT)"
	@ python -m pip install --upgrade pip
	@ python -m pip install ".[dev]"

install-dev:
	@ echo -e "$(BUILD_PRINT)Installing the package (editable) with its dev extra$(END_BUILD_PRINT)"
	@ python -m pip install --upgrade pip
	@ python -m pip install -e ".[dev]"


install:
	@ echo "$(BUILD_PRINT)Installing the package (runtime only)"
	@ python -m pip install --upgrade pip
	@ python -m pip install .


test: test-unit


test-unit:
	@ echo -e "$(BUILD_PRINT)Unit Testing ...$(END_BUILD_PRINT)"
	@ tox -e unit


test-features:
	@ echo -e "$(BUILD_PRINT)Gherkin Features Testing ...$(END_BUILD_PRINT)"
	@ tox -e features


test-all:
	@ echo "$(BUILD_PRINT)Running all tests (excludes live-network tests)"
	@ tox

test-network:
	@ echo -e "$(BUILD_PRINT)Running live-network integration tests (need network)$(END_BUILD_PRINT)"
	@ tox -e network


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
	@ py.test --generate-missing --feature $(FEATURES_FOLDER)

$(addprefix $(STEPS_FOLDER)/test_, $(notdir $(STEPS_FOLDER)/%.py)): $(FEATURES_FOLDER)/%.feature
	@ echo "$(BUILD_PRINT)Generating the testfile "$@"  from "$<" feature file"
	@ pytest-bdd generate $< > $@
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

build:
	@ echo "$(BUILD_PRINT)Building the sdist and wheel (PEP 517 via python -m build)"
	@ rm -rf dist
	@ python -m build

publish-pipy: build
	@ echo "$(BUILD_PRINT)Checking the distribution"
	@ twine check dist/*
	@ echo "$(BUILD_PRINT)Uploading the distribution"
	@ twine upload --skip-existing dist/*

#-----------------------------------------------------------------------------
# Default
#-----------------------------------------------------------------------------
all: install test
