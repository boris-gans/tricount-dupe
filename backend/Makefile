# Tell make that these targets are commands, not files
.PHONY: test coverage clean

# Use the current Python/venv
PYTHON := python3

# Directory where HTML coverage will be written
COV_HTML_DIR := htmlcov

test:
	$(PYTHON) -m pytest tests/

coverage:
	$(PYTHON) -m pytest \
		--cov=app \
		--cov-report=html \
		--cov-report=term \
		--cov-report=xml:coverage.xml \
		--cov-fail-under=80 \
		tests/
	@echo "HTML coverage report generated at $(COV_HTML_DIR)/index.html"
	@echo "XML coverage report generated at coverage.xml"

clean:
	rm -rf $(COV_HTML_DIR)
	rm -rf .coverage
