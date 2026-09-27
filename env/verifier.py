"""Verifier: reads only the final state and returns 1 (solved) or 0 (not solved).

Each check returns a list of human-readable failure reasons (empty = passed).
"""

from .cnc_env import CNCSchedulingEnv


def verify(state):
    """Return 1 if the schedule is complete, compatible, overlap-free, on time and replayable."""
    return explain(state)[0]


def explain(state):
    """Return (score, reasons): score is 0 or 1, reasons lists every failed check."""
    if state["invalid"]:
        return 0, [f"invalid action taken: {state['action_log'][-1]}"]
    checks = [_all_jobs_once, _compatible, _no_overlap, _on_time, _replays]
    reasons = [r for check in checks for r in check(state)]
    return int(not reasons), reasons


def _all_jobs_once(state):
    """Every job appears exactly once in the schedule."""
    scheduled = [s["job_id"] for s in state["schedule"]]
    reasons = []
    for job in state["jobs"]:
        count = scheduled.count(job["id"])
        if count != 1:
            reasons.append(f"job {job['id']} scheduled {count} times (expected 1)")
    known = {j["id"] for j in state["jobs"]}
    reasons += [f"unknown job {j} in schedule" for j in set(scheduled) - known]
    return reasons


def _compatible(state):
    """Each part fits its machine and the machine has enough axes."""
    jobs = {j["id"]: j for j in state["jobs"]}
    machines = {m["id"]: m for m in state["machines"]}
    reasons = []
    for s in state["schedule"]:
        job, machine = jobs.get(s["job_id"]), machines.get(s["machine_id"])
        if job is None:
            continue  # reported by _all_jobs_once
        if machine is None:
            reasons.append(f"job {job['id']} on unknown machine {s['machine_id']}")
            continue
        if job["part_size"] > machine["max_part_size"]:
            reasons.append(
                f"job {job['id']}: part size {job['part_size']} too big for "
                f"machine {machine['id']} (max {machine['max_part_size']})"
            )
        if job["axes_needed"] > machine["axes"]:
            reasons.append(
                f"job {job['id']}: needs {job['axes_needed']} axes, "
                f"machine {machine['id']} has {machine['axes']}"
            )
    return reasons


def _no_overlap(state):
    """No two jobs run on the same machine at the same time."""
    by_machine = {}
    for s in state["schedule"]:
        by_machine.setdefault(s["machine_id"], []).append(s)
    reasons = []
    for machine_id, slots in by_machine.items():
        slots.sort(key=lambda s: s["start"])
        for a, b in zip(slots, slots[1:]):
            if b["start"] < a["end"]:
                reasons.append(
                    f"machine {machine_id}: job {a['job_id']} [{a['start']}, {a['end']}) "
                    f"overlaps job {b['job_id']} [{b['start']}, {b['end']})"
                )
    return reasons


def _on_time(state):
    """Every job finishes by its deadline and runs for exactly its duration."""
    jobs = {j["id"]: j for j in state["jobs"]}
    reasons = []
    for s in state["schedule"]:
        job = jobs.get(s["job_id"])
        if job is None:
            continue
        if s["end"] - s["start"] != job["duration"]:
            reasons.append(
                f"job {job['id']}: runs {s['end'] - s['start']} units, duration is {job['duration']}"
            )
        if s["end"] > job["deadline"]:
            reasons.append(
                f"job {job['id']}: finishes at {s['end']}, deadline {job['deadline']} "
                f"(late by {s['end'] - job['deadline']})"
            )
    return reasons


def _replays(state):
    """Replaying the action log in a fresh env must give the same schedule.

    Blocks a final state that was written directly instead of reached through step().
    """
    env = CNCSchedulingEnv(state["jobs"], state["machines"])
    for action in state["action_log"]:
        if env.done:
            return ["action log has actions after the episode ended"]
        env.step(tuple(action))
    if env.invalid:
        return ["action log contains an invalid action"]
    if env.schedule != state["schedule"]:
        return ["schedule does not match a replay of the action log (state was edited directly)"]
    return []
