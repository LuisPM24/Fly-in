GREEN = \033[1;32m
YELLOW = \033[1;33m
RESET = \033[0m

install:
	uv sync

run:
	@echo "$(YELLOW) Running 'make run' command$(RESET)\n"
	@uv run python -m main
	@echo "$(GREEN)\n'make run' command completed$(RESET)"

debug:
	@echo "$(YELLOW) Running 'make debug' command$(RESET)\n"
	@uv run python -m pdb -m main
	@echo "$(GREEN)\n'make debug' command completed$(RESET)"

test:
	@echo "$(YELLOW)\nRunning 'make test' command $(RESET)\n"
	@uv run python -m pytest -s -p no:terminal || true
	@echo "$(GREEN)\n'make test' command completed$(RESET)"

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache
	@echo "$(GREEN)\n'make clean' command completed$(RESET)"

lint:
	@echo "$(YELLOW)\nRunning 'make lint' command $(RESET)\n"
	@uv run flake8 .
	@uv run mypy . 	--warn-return-any --warn-unused-ignores \
					--ignore-missing-imports --disallow-untyped-defs \
					--check-untyped-defs

.PHONY: install run debug test clean lint