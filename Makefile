.DEFAULT_GOAL := help

# Set python
export PYTHONPATH=.
python = python

.PHONY: help
help:
	@echo "USAGE"
	@echo "  make <commands>"
	@echo ""
	@echo "AVAILABLE COMMANDS"
	@echo "  - PRODUCTION - "
	@echo "  install 		Install the dependencies"
	@echo "  start_chat 	Start the chat in interactive mode"
	@echo "  start_service  Start the FastAPI service"
	@echo "  start_docker_fastapi  Start the FastAPI service in docker"
	@echo "  start_bot		Start the TG bot"
	@echo " "
	@echo "  - DEVELOPMENT -"
	@echo "  lint			Reformat code"
	@echo "  install_dev	Install the dependencies for development"


# ================================================================================================
# Dependencies
# ================================================================================================

.PHONY: install
install:
	$(python) -m pip install -r requirements/prod.txt

.PHONY: install_dev
install_dev:
	$(python) -m pip install -r requirements/dev.txt


# ================================================================================================
# Lint
# ================================================================================================

.PHONY:	black
black:
	$(python) -m black --line-length 80 .

.PHONY: isort
isort:
	$(python) -m isort .

.PHONY: flake
flake:
	$(python) -m flake8 .

.PHONY: lint
lint: black isort flake


# ================================================================================================
# Start
# ================================================================================================

.env:
	# Check if .env file exists
	@echo "ERROR: You need to specify TOKENS in .env file. Read README.md for more info."
	exit 1

.PHONY: start_chat
start_chat: .env
	@echo "Running chat..."
	$(python) src/answerer.py

.PHONY: start_service
start_service: .env
	@echo "Running service..."
	$(python) src/main.py

.PHONY: start_bot
start_bot: .env
	@echo "Running bot..."
	$(python) src/bot.py

.PHONY: start_docker_fastapi
start_docker_fastapi:
	@echo "Running docker FastAPI..."
