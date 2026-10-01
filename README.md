# TGDC Case Study

A small RL-style environment for scheduling CNC machining jobs, with a variant generator, a verifier and two baseline agents.

## Layout

- `env/cnc_env.py` — the environment
- `env/generator.py` — builds variants around a planted solution, so each one is solvable. Presets: `easy`, `medium1`, `medium2`, `hard1`, `hard2`, plus seeded random variants
- `env/verifier.py` — `verify(state)` and `explain(state)` (score plus failure reasons)
- `agents/` — `GreedyAgent` (ignores constraints) and `GreedyAgentSophisticated` (respects size/axes, ignores deadlines)
- `run.py` — runs both agents on all variants and prints success rates
- `NOTE.md` — one-page note: decisions, results, limits, next step
- `TGDC_Case_Study.pdf` — case study brief; `my_notes.md` — working notes

## Usage

```
pip install -r requirements.txt      # only needed for the tests (pytest)
python run.py                        # presets + 100 random variants (seeds 0-99), summary at the end
python run.py 42                     # random variants from seed 42 instead
python run.py explanation=true       # also print why each episode failed
```

Tests: `python -m pytest` (verifier tests in `tests/test_verifier.py`, exploit tests in `tests/test_reward.py`).

The number of random variants is set by `N_RANDOM` in `run.py`.
