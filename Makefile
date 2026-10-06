.PHONY: setup agent test-weeks

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	cp -n .env.example .env || true
	@echo "Done. Edit .env with your API key, then run: make agent"

agent:
	.venv/bin/python agent/agent.py --demo

test-weeks:
	@echo "TODO: wire per-week eval suites here as the course progresses."
