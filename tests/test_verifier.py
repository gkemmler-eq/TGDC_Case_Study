"""Verifier tests: initial state scores 0, correct solution scores 1,
invalid actions and directly written goal states score 0."""

import copy

import pytest

from env import PRESETS, CNCSchedulingEnv, explain, preset, random_variant

VARIANTS = [preset(name) for name in PRESETS] + [random_variant(s) for s in range(10)]
IDS = list(PRESETS) + [f"random{s}" for s in range(10)]

# Tiny hand-built variant for targeted checks: one small 3-axis machine, one big 5-axis machine.
MACHINES = [
    {"id": 0, "max_part_size": 1, "axes": 3},
    {"id": 1, "max_part_size": 3, "axes": 5},
]
JOBS = [
    {"id": 0, "duration": 2, "part_size": 1, "axes_needed": 3, "deadline": 2},
    {"id": 1, "duration": 3, "part_size": 3, "axes_needed": 5, "deadline": 3},
]


def play(jobs, machines, actions):
    """Step through the actions in a fresh env and return its final state."""
    env = CNCSchedulingEnv(jobs, machines)
    for action in actions:
        env.step(action)
    return env.final_state()


def solved(v):
    return play(v["jobs"], v["machines"], v["solution"])


# --- required by the brief --------------------------------------------------


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_initial_state_scores_0(v):
    state = CNCSchedulingEnv(v["jobs"], v["machines"]).final_state()
    score, reasons = explain(state)
    assert score == 0
    assert any("scheduled 0 times" in r for r in reasons)


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_correct_solution_scores_1(v):
    assert explain(solved(v)) == (1, [])


@pytest.mark.parametrize(
    "actions",
    [[(999, 0)], [(0, 999)], [(0, 1), (0, 1)], ["not an action"]],
    ids=["unknown_job", "unknown_machine", "job_twice", "malformed"],
)
def test_invalid_action_scores_0(actions):
    state = play(JOBS, MACHINES, actions)
    assert state["invalid"]
    assert explain(state)[0] == 0


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_goal_state_without_actions_scores_0(v):
    state = solved(v)
    state["action_log"] = []
    score, reasons = explain(state)
    assert score == 0
    assert any("replay" in r for r in reasons)


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_handwritten_goal_state_scores_0(v):
    """A perfect schedule written directly, never reached through step()."""
    free = {m["id"]: 0 for m in v["machines"]}
    jobs = {j["id"]: j for j in v["jobs"]}
    schedule = []
    for job_id, machine_id in v["solution"]:
        start = free[machine_id]
        free[machine_id] = start + jobs[job_id]["duration"]
        schedule.append(
            {"job_id": job_id, "machine_id": machine_id, "start": start, "end": free[machine_id]}
        )
    state = {
        "jobs": copy.deepcopy(v["jobs"]),
        "machines": copy.deepcopy(v["machines"]),
        "schedule": schedule,
        "action_log": [],
        "invalid": False,
    }
    assert schedule == solved(v)["schedule"]  # the schedule itself is correct
    assert explain(state)[0] == 0


# --- one test per remaining check ------------------------------------------


def test_incompatible_machine_scores_0():
    # Job 1 (size 3, 5 axes) on the small machine.
    score, reasons = explain(play(JOBS, MACHINES, [(0, 1), (1, 0)]))
    assert score == 0
    assert any("too big" in r for r in reasons)
    assert any("axes" in r for r in reasons)


def test_late_job_scores_0():
    # Both jobs on the big machine: job 1 then finishes at 5, deadline 3.
    score, reasons = explain(play(JOBS, MACHINES, [(0, 1), (1, 1)]))
    assert score == 0
    assert any("late by" in r for r in reasons)


def test_hand_solution_scores_1():
    assert explain(play(JOBS, MACHINES, [(0, 0), (1, 1)])) == (1, [])


def test_tampered_times_score_0():
    state = play(JOBS, MACHINES, [(0, 1), (1, 1)])
    state["schedule"][1]["start"] = 0  # squeeze job 1 alongside job 0
    state["schedule"][1]["end"] = 3
    score, reasons = explain(state)
    assert score == 0
    assert any("overlaps" in r for r in reasons)
    assert any("replay" in r for r in reasons)


def test_wrong_duration_scores_0():
    state = play(JOBS, MACHINES, [(0, 0), (1, 1)])
    state["schedule"][1]["end"] = 1
    score, reasons = explain(state)
    assert score == 0
    assert any("duration is" in r for r in reasons)


@pytest.mark.parametrize("v", VARIANTS, ids=IDS)
def test_partial_schedule_scores_0(v):
    state = play(v["jobs"], v["machines"], v["solution"][:-1])
    assert explain(state)[0] == 0
