.PHONY: setup agent test-weeks

setup:
	@echo "[1/3] Creating virtualenv (.venv)..."
	python3 -m venv .venv
	@echo "[2/3] Installing core packages (takes 3-5 min — hang tight, don't Ctrl-C)..."
	.venv/bin/pip install -r requirements.txt
	@echo "[3/3] Setting up .env..."
	cp -n .env.example .env || true
	@echo "Done. Edit .env with your API key, then run: make agent"

agent:
	.venv/bin/python agent/agent.py --demo

agent-demo: agent  # alias used in the Week 1 assignment doc

test-weeks:
	@echo "TODO: wire per-week eval suites here as the course progresses."
