# TGDC Case Study

A small RL-style environment for scheduling CNC machining jobs, with a variant generator, a verifier and two baseline agents.

## The task

Each job (`duration`, `part_size`, `axes_needed`, `deadline`) must be assigned to a machine (`max_part_size`, `axes`). An action `(job_id, machine_id)` appends the job to that machine's queue. The episode ends when every job is scheduled.

- **Reward:** +1 per job that finishes on time on a compatible machine, −1 (and episode ends) for an illegal action.
- **Exploit:** the original ("naive") reward ignored compatibility, so a wrong schedule could earn full reward. It is kept as `CNCSchedulingEnv(..., reward="naive")` for comparison; `tests/test_reward.py` proves the fix.
- **Verifier:** scores the final state 1 or 0. It passes only if every job is scheduled once, on a compatible machine, without overlaps, on time, and the schedule matches a replay of the action log.

## Layout

- `env/cnc_env.py` — the environment
- `env/generator.py` — builds variants around a planted solution, so each one is solvable. Presets: `easy`, `medium1`, `medium2`, `hard1`, `hard2`, plus seeded random variants
- `env/verifier.py` — `verify(state)` and `explain(state)` (score plus failure reasons)
- `agents/` — `GreedyAgent` (ignores constraints) and `GreedyAgentSophisticated` (respects size/axes, ignores deadlines)
- `run.py` — runs both agents on all variants and prints success rates
- `TGDC_Case_Study.pdf` — case study brief; `my_notes.md` — working notes

## Usage

```
python run.py                        # all presets
python run.py 42                     # fixed seed for random variants
python run.py explanation=true       # also print why each episode failed
```

Tests: `python -m pytest` (verifier tests in `tests/test_verifier.py`, exploit tests in `tests/test_reward.py`).

The number of random variants is set by `N_RANDOM` in `run.py`.
