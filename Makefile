.PHONY: setup setup-extra agent test-weeks

setup:
	@echo "[1/3] Creating virtualenv (.venv)..."
	python3 -m venv .venv
	@echo "[2/3] Installing core packages (takes 3-5 min — hang tight, don't Ctrl-C)..."
	.venv/bin/pip install -r requirements.txt
	@echo "[3/3] Setting up .env..."
	cp -n .env.example .env || true
	@echo "Done. Edit .env with your API key, then run: make agent"
	@echo "Heavier week-specific deps (deepeval, ragas) come later: make setup-extra"

setup-extra:
	@echo "Installing week-specific packages (deepeval, ragas — needed from Week 2/4 onward)..."
	@echo "(This one is slow too — grab a coffee.)"
	.venv/bin/pip install -r requirements-extra.txt
	@echo "Done. Week 3 also needs promptfoo (Node): npm install -g promptfoo"

agent:
	.venv/bin/python agent/agent.py --demo

test-weeks:
	@echo "TODO: wire per-week eval suites here as the course progresses."
